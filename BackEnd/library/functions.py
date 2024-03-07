from library.settings import vectordb

def retrieve_answer(question):
    return vectordb.get_sql(question)
