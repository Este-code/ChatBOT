from fastapi import FastAPI, UploadFile, File, status, HTTPException
import tempfile
import library.functions as fn
from models.question import QuestionInput
import library.settings

app = FastAPI()

@app.get("/")
async def root():
    return {"Greetings" : "Welcome to chatBot for general purposes."}

@app.post("/upload/", status_code=status.HTTP_200_OK)
async def upload(file : UploadFile = File(...)):

    # Check if the file is empty
    if file.file is None:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        # Save the PDF file to a temporary location
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(await file.read())
            pdf_path = temp_file.name
            fn.store_document(pdf_path)

        return {"message": "File uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@app.post("/qa/", status_code=status.HTTP_200_OK)
async def question_and_answer(question : QuestionInput):
    try:
        answer = fn.retrieve_answer_using_base_prompt(question.question)
        return {"question": question.question, "answer": answer["result"]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 