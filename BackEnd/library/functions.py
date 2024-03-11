from library.settings import vectordb
from library.settings import bufferMemory

def retrieve_answer(question):
    response = vectordb.retrieve_sql(question)
    if(len(response)>0):
        bufferMemory.add_memory(question, response[1])
    else:
        bufferMemory.add_memory(question, "No answer.")

    return response
