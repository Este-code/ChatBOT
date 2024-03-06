from fastapi import FastAPI, status, HTTPException
import uvicorn
import library.functions as fn
from models.RetrieveSQL import RetrieveSQL
from library.settings import cursor, conn, data, embedding
import library.CustomVectorDB as vectordb

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

    #vectordb.add_sql(data)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)