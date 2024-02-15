from fastapi import FastAPI, UploadFile, File, status, HTTPException
import uvicorn
import library as lbr

app = FastAPI()

@app.post("/upload/", status_code=status.HTTP_200_OK)
async def upload(file : UploadFile = File()):
    try:
        content = await file.read()
        lbr.store_document(content)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@app.post("/qa/", status_code=status.HTTP_200_OK)
async def question_and_answer(question : str):
    try:
        answer = lbr.retrieve_answer_using_base_prompt(question)
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

