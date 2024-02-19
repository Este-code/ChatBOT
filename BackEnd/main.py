from fastapi import FastAPI, UploadFile, File, status, HTTPException
from PyPDF2 import PdfReader
from io import BytesIO
import library as lbr

app = FastAPI()

@app.get("/")
async def root():
    return {"Greetings" : "Welcome to chatBot for general purposes."}

@app.post("/upload/", status_code=status.HTTP_200_OK)
async def upload(file : UploadFile = File(...)):
    try:
        content = await file.read()
        # Use BytesIO to create a file-like object from the PDF contents
        pdf_stream = BytesIO(content)
        # Pass the PDF stream to PyPDF2's PdfReader
        pdf_reader = PdfReader(pdf_stream)
        # Extract text from each page using PyPDF2
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            
        lbr.store_document(text)
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