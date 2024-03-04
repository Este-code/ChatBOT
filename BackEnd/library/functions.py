import library.CustomVectorDB as vectordb

def retrieve_answer(question):
    return vectordb.retrieve_sql(question)
