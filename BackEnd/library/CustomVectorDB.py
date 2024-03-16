from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm
import sqlite3
import os
import pdfquery
from docx2python import docx2python

class CustomVectorDB:
    # Classe CustomVectorDB necessita del percorso di una cartella esistente per essere inizializzata
    # Se non esiste, il db sqlite viene creato
    # Se non esiste, la tabella sql_queries viene creata con i campi (id, sql, metadata, vector)
    # Se non esiste, la tabella doc_queries viene creata con i campi (id, title, testo, metadata, vector)
    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

        self.conn = sqlite3.connect(os.path.join(path, 'vector_db.sqlite'), check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.embedding = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sql_queries (
                        id INTEGER PRIMARY KEY,
                        sql TEXT,
                        metadata TEXT,
                        vector TEXT
                    )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS doc_queries (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        metadata TEXT,
                        testo TEXT,
                        vector TEXT
                    )''')
        self.conn.commit()

    #--------------------------------- RETREIVE BEGIN ---------------------------------------------

    # Funzione che prende in input la query e il valore di soglia (opzionale)
    # Se trova più di 5 risultati restituisce i primi 5 risultati con indice di similarità pi
    # In ordine restituisce ID, TITLE, TESTO, METADATA, SIMILARITY
    # Restituisce una lista vuota se non trova nulla
    def retrieve_docs(self, input_sentence, threshold=0.6):
        input_vector = self.embedding.encode(input_sentence.lower())
        self.cursor.execute('''SELECT id, title, testo, metadata, vector FROM doc_queries''')
        results = self.cursor.fetchall()
        relevant_results = []
        for result in results:
            stored_vector = json.loads(result[4])
            similarity = cosine_similarity([input_vector], [stored_vector])[0][0]
            if similarity > threshold:
                relevant_results.append([result[0], result[1], result[2], result[3], similarity])

        if len(relevant_results) > 1:
            relevant_results = sorted(relevant_results, key=lambda x: x[4], reverse=True)

        if len(relevant_results) >= 5:
            return relevant_results[0:5]
        else:
            return relevant_results
    
    # Funzione che prende in input la query e il valore di soglia (opzionale)
    # Se trova più di un risultato restituisce il record con la similarità più alta
    # In ordine restituisce ID, SQL, METADATA, SIMILARITY
    # Restituisce una lista vuota se non trova nulla
    def retrieve_sql(self, input_sentence, threshold=0.6):
        input_vector = self.embedding.encode(input_sentence.lower())
        self.cursor.execute('''SELECT id, sql, metadata, vector FROM sql_queries''')
        results = self.cursor.fetchall()
        relevant_results = []
        for result in results:
            stored_vector = json.loads(result[3])
            similarity = cosine_similarity([input_vector], [stored_vector])[0][0]
            if similarity > threshold:
                relevant_results.append([result[0], result[1], result[2], similarity])

        if len(relevant_results) >= 1:
            relevant_results = sorted(relevant_results, key=lambda x: x[3], reverse=True)
            return relevant_results[0]
        else:
            return relevant_results

    #--------------------------------- RETREIVE END ---------------------------------------------
    
    #--------------------------------- ADD BEGIN ---------------------------------------------

    def add_pdf(self, documents_directory,filename):
        pdf = pdfquery.PDFQuery(f"{documents_directory}/{filename}")
        pdf.load()
        num_pages = len(pdf.pq('LTPage'))
        for page_number in tqdm(range(num_pages), desc=f"Reading: {filename}"):
            text_elements = pdf.pq(f'LTPage[pageid="{page_number + 1}"] LTTextLineHorizontal')
            text = [t.text for t in text_elements]
            text = ' '.join(text)
            text = text.strip()
            if len(text) == 0:
                continue
            vector = self.embedding.encode(text)
            vector_list = [i for i in vector]
            metadata = {"filename": filename, "page_number": page_number + 1}
            self.cursor.execute('''INSERT INTO doc_queries (title,testo, metadata, vector) VALUES (?, ?, ?, ?)''',
                                (filename, text, str(metadata), str(vector_list)))
        self.conn.commit()


    def add_docx(self, documents_directory,filename):
        page_number = 0
        doc = docx2python(f"{documents_directory}/{filename}")
        text = doc.text
        text = text.strip()
        # skip empty text
        if len(text) == 0:
            return
        # Split text every 2250 characters and put it in text_arr
        for i in tqdm(range(0, len(text), 2250), desc=f"Reading: {filename}"):
            page_number += 1
            cleaned_text = str(text[i:i + 2250]).replace("\xa0", " ")
            vector = self.embedding.encode(cleaned_text)
            vector_list = [i for i in vector]
            metadata = {"filename": filename, "page_number": page_number + 1}
            self.cursor.execute('''INSERT INTO doc_queries (title,testo, metadata, vector) VALUES (?, ?, ?, ?)''',
                                (filename, cleaned_text, str(metadata), str(vector_list)))
        self.conn.commit()

    
    def add_txt(self, documents_directory, filename):
        try:
            with open(f"{documents_directory}/{filename}", "r", encoding="utf-8") as file:
                buffer = []
                for chunk, line in enumerate(tqdm((file.readlines()), desc=f"Reading: {filename}"), 1):
                    # Strip whitespace and append the line to the buffer
                    line = line.strip()
                    # Skip empty lines
                    if len(line) == 0:
                        continue
                    buffer.append(line)

                    # If the buffer has 20 lines, join them with a newline and append to the documents list
                    if len(buffer) == 20:
                        vector = self.embedding.encode("\n".join(buffer))
                        vector_list = [i for i in vector]
                        metadata = {"filename": filename, "chunk": chunk}
                        self.cursor.execute('''INSERT INTO doc_queries (title,testo, metadata, vector) VALUES (?, ?, ?, ?)''',
                                (filename, "\n".join(buffer), str(metadata), str(vector_list)))
                        # Clear the buffer
                        buffer = []
                    # If the buffer is not empty, append the remaining lines to the documents list
                    if buffer:
                        vector = self.embedding.encode("\n".join(buffer))
                        vector_list = [i for i in vector]
                        metadata = {"filename": filename, "chunk": chunk}
                        self.cursor.execute('''INSERT INTO doc_queries (title,testo, metadata, vector) VALUES (?, ?, ?, ?)''',
                                (filename, "\n".join(buffer), str(metadata), str(vector_list)))
                    
                self.conn.commit()
        except Exception as e:
            print("ERROR: "+str(e))
    
    # Funzione che prende in input una lista di json annidati per inserimento in banca dati
    # Vedere il file training.json come riferimento per struttura json
    # NB: da implementare gestione di errore (es. viene un json con una struttura che non corrisponde a quella utilizzata al momento)
    def add_sql(self, data):
        for i, doc in enumerate(data):
            vector = self.embedding.encode(doc['metadata'].lower())
            vector_list = [i for i in vector]
            self.cursor.execute('''INSERT INTO sql_queries (sql, metadata, vector) VALUES (?, ?, ?)''',
                                (doc['sql'], doc['metadata'], str(vector_list)))
        self.conn.commit()

    #--------------------------------- ADD END ---------------------------------------------
    
    #--------------------------------- DELETE BEGIN ---------------------------------------------
    
    # Funzione che prende in input lista di ids per eliminazione di record in banca dati
    # Introdotto parametro multiple delete, impostato di default a False
    # Con multiple delete a false, il parametro ids deve essere solamente il singolo id (stringa o numero)
    # Se multiple delete è impostato a true, ids deve essere una lista di id
    # NB: da implementare gestione di errore (es. viene passato un id che non esiste)
    def delete_docs(self,titles, multiple_delete=False):
        if multiple_delete:
            for i in titles:
                self.cursor.execute('DELETE FROM doc_queries WHERE title = '+i)
            self.conn.commit()
        else:
            self.cursor.execute('DELETE FROM doc_queries WHERE title = '+titles)
            self.conn.commit()
    
    # Funzione che prende in input lista di ids per eliminazione di record in banca dati
    # Introdotto parametro multiple delete, impostato di default a False
    # Con multiple delete a false, il parametro ids deve essere solamente il singolo id (stringa o numero)
    # Se multiple delete è impostato a true, ids deve essere una lista di id
    # NB: da implementare gestione di errore (es. viene passato un id che non esiste)
    def delete_sql(self,ids, multiple_delete=False):
        if multiple_delete:
            for i in ids:
                self.cursor.execute('DELETE FROM sql_queries WHERE id = '+i)
            self.conn.commit()
        else:
            self.cursor.execute('DELETE FROM sql_queries WHERE id = '+ids)
            self.conn.commit()

    #--------------------------------- DELETE END ---------------------------------------------
    
    #--------------------------------- GET BEGIN ---------------------------------------------

    # Funzione che restituisce tutti i titoli dei documenti presenti in banca dati
    # Informazioni restituite: title
    # Restituisce un oggetto vuoto se non ci sono record
    def getAll_docs(self):
        self.cursor.execute('''SELECT DISTINCT title FROM doc_queries''')
        results = self.cursor.fetchall()
        if(len(results)>0):
            doc_json = json.dumps([{
                'title': row[0],
            } for row in results])
            return doc_json
        else:
            return []
    
    def get_doc(self, title):
        self.cursor.execute("SELECT DISTINCT title FROM doc_queries WHERE title LIKE '"+title+"';" )
        results = self.cursor.fetchall()
        if(len(results)>0):
            doc_json = json.dumps([{
                'title': row[0],
            } for row in results])

            return doc_json
        else:
            return []
    
    # Funzione che restituisce tutte i record presenti in banca dati
    # Informazioni restituite: ID, SQL, METADATA
    # Restituisce un oggetto vuoto se non ci sono record
    def getAll_sql(self):
        self.cursor.execute('''SELECT id, sql, metadata FROM sql_queries''')
        results = self.cursor.fetchall()
        if(len(results)>0):
            sql_json = json.dumps([{
                'id': row[0],
                'sql': row[1],
                'metadata': row[2]
            } for row in results])

            return sql_json
        else:
            return []
    
    #--------------------------------- GET END ---------------------------------------------
