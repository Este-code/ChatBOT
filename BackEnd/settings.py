import openai
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv, find_dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

persist_directory = "./chroma"


load_dotenv(find_dotenv()) # reads local .env file

embedding = OpenAIEmbeddings()

openai.api_key = os.environ['OPENAI_API_KEY']

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature = 0)

compressor = LLMChainExtractor.from_llm(llm)

vectordb = Chroma(
    collection_name="chatbot",
    persist_directory=persist_directory,
    embedding_function=embedding
)

compressor_retreiver = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectordb.as_retriever()
)

# Build prompt
template = """
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum. Keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer. 
    {context}
    Question: {question}
    Helpful Answer:
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

# Run chain
qa = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)


'''

memory integration TO BE TESTED

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
qa = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=vectordb.as_retriever(),
    memory=memory
)
'''
