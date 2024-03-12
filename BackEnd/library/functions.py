from library.settings import vectordb
from library.settings import bufferMemory

def retrieve_answer(question):
    response = vectordb.retrieve_sql(question)
    if(len(response)>0):
        bufferMemory.add_memory('admin',question, response[1])


    return response
