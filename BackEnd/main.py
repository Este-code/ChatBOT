from fastapi import FastAPI, UploadFile, File, status, HTTPException
import library as lbr
import tempfile
from question import QuestionInput

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
            lbr.store_document(pdf_path)

        return {"message": "File uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@app.post("/qa/", status_code=status.HTTP_200_OK)
async def question_and_answer(question : QuestionInput):
    try:
        answer = lbr.retrieve_answer_using_base_prompt(question.question)
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 