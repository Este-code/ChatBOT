from fastapi import FastAPI, status, HTTPException
import uvicorn
import library.functions as fn
from models.RetrieveSQL import RetrieveSQL
import json
from library.settings import vectordb
from library.settings import bufferMemory

app = FastAPI()

@app.post("/getsql/", status_code=status.HTTP_200_OK)
async def question_and_answer(query : RetrieveSQL):
    try:
        answer = fn.retrieve_answer(query.query)
        return {"question": query.query, "answer": answer}
    except Exception as e:
        print("ERROR: "+str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    
@app.post("/getMemories/", status_code=status.HTTP_200_OK)
def getMemories():
    try:
        history = bufferMemory.get_memories('admin')
        return history
    except Exception as e:
        print("ERROR: "+str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

if __name__ == "__main__":
    
    #Test inserimento dati
    #with open('config/training.json', encoding="utf-8")as file:
    #    data = json.load(file)
    #vectordb.add_sql(data)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)