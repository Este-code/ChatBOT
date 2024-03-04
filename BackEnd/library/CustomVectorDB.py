from sklearn.metrics.pairwise import cosine_similarity
import json
from library.settings import cursor, conn, embedding

def retrieve_sql(input_sentence, threshold=0.8):
    input_vector = embedding.encode(input_sentence.lower())
    cursor.execute('''SELECT sql, metadata, vector FROM sql_queries''')
    results = cursor.fetchall()
    relevant_results = []
    for result in results:
        stored_vector = json.loads(result[2])
        similarity = cosine_similarity([input_vector], [stored_vector])[0][0]
        if similarity > threshold:
            relevant_results.append((result[0], result[1], similarity))
    return relevant_results

def add_sql(data):
    for i, doc in enumerate(data):
        vector = embedding.encode(doc['metadata'].lower())
        vector_list = [i for i in vector]
        cursor.execute('''INSERT INTO sql_queries (sql, metadata, vector) VALUES (?, ?, ?)''', (doc['sql'], doc['metadata'], str(vector_list)))
    conn.commit()

def delete_sql(ids):
    for i in ids:
        cursor.execute('DELETE FROM sql_queries WHERE id = '+i)
    conn.commit()