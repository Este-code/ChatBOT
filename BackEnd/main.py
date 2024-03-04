from fastapi import FastAPI, status, HTTPException
import uvicorn
import library.functions as fn
from models.RetrieveSQL import RetrieveSQL
from library.settings import cursor, conn, data, embedding

app = FastAPI()

@app.post("/getsql/", status_code=status.HTTP_200_OK)
async def question_and_answer(query : RetrieveSQL):
    try:
        answer = fn.retrieve_answer(query.query)
        return {"question": query.query, "answer": answer}
    except Exception as e:
        print("ERROR: "+str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    

if __name__ == "__main__":
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS sql_queries (
                    id INTEGER PRIMARY KEY,
                    sql TEXT,
                    metadata TEXT,
                    vector TEXT
                )''')
    conn.commit()

    for i, doc in enumerate(data):
        vector = embedding.encode(doc['metadata'].lower())
        vector_list = [i for i in vector]
        cursor.execute('''INSERT INTO sql_queries (sql, metadata, vector) VALUES (?, ?, ?)''', (doc['sql'], doc['metadata'], str(vector_list)))
    conn.commit()

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)