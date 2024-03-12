import mysql.connector
import json

#Classe ConversationBufferMemory necessita dei seguenti parametri 
# per essere inizializzata : host, user, password di mysql 
# Questa classe provvede a creare il db se non esiste
# Inoltre crea la tabella ConversationBufferMemmory se non esiste
class ConversationBufferMemory:
    def __init__(self, host, user, password):
        self.mysqldb = mysql.connector.connect(
            host = host,
            user = user,
            password = password
        )
        self.cursor = self.mysqldb.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS `3AAI`;")
        self.cursor.execute("USE `3AAI`;")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ConversationBufferMemory (
                        id INT NOT NULL AUTO_INCREMENT,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        user VARCHAR(500),
                        topic TEXT,
                        request TEXT,
                        response TEXT,
                        PRIMARY KEY (id)
                );''')
        self.mysqldb.commit()
    
    # Metodo per inserimento di una nuova 'memoria'
    # Necessita di 4 parametri obbligatori:
    # user = utente che ha generato la richiesta
    # topic = oggetto della richiesta
    # request = richiesta inoltrata dall'utente
    # response = risposta ottenuta
    def add_memory(self, user, topic, request, response):
        try:
            sql = "INSERT INTO 3AAI.ConversationBufferMemory(user, topic, request, response) VALUES (%s, %s, %s, %s);"
            val = (user, topic, request, response)
            self.cursor.execute(sql,val)
            self.mysqldb.commit()
        except Exception as e:
            print("ConversationBufferMemory Error: "+str(e))
    
    # Metodo per la restituizione delle 'memorie'
    # Prende in input un parametro obbligatorio: User
    # Prende in input un parametro opzionale: topic
    # Se topic non è valorizzato, ritorna tutto ciò che è collegato allo user indicato
    def get_memories(self, user, topic='%'):
        self.cursor.execute("SELECT * FROM 3AAI.ConversationBufferMemory WHERE user LIKE '"+user+"' AND topic LIKE '"+topic+"';")
        results = self.cursor.fetchall()

        # Convert the fetched data into a JSON format
        memories_json = json.dumps([{
            'id': row[0],
            'timestamp': row[1].isoformat(),  # Convert timestamp to ISO format
            'user': row[2],
            'topic': row[3],
            'request': row[4],
            'response': row[5]
        } for row in results])

        return memories_json
