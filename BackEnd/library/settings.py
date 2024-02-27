import openai
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv, find_dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.document_loaders import JSONLoader
#from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.lancedb import LanceDB
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from sqlalchemy import create_engine
from library.common import get_config_value
from library.ddl import ddl
load_dotenv(find_dotenv()) # reads local .env file

#persist_directory = "./chroma"

dati_connessione = get_config_value("dati_connessione")
engine = create_engine(dati_connessione)


embedding = OpenAIEmbeddings()
openai.api_key = os.environ['OPENAI_API_KEY']
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature = 0)



'''
vectordb = Chroma(
    collection_name="chatbot",
    persist_directory=persist_directory,
    embedding_function=embedding
)
'''
vectordb = LanceDB(
    embedding=embedding
)

# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["question"] = record.get("question")
    return metadata

initial_training = JSONLoader(
    file_path='./config/training.json',
    jq_schema='.[]',
    content_key='sql',
    text_content=False,
    metadata_func=metadata_func
).load()

vectordb.add_documents(
    documents=initial_training
)

compressor = LLMChainExtractor.from_llm(llm)
compressor_retreiver = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectordb.as_retriever()
)
'''
# Build prompt
template = """
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum. Keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer.
    Include metadata in the answer.
    {context}
    Question: {question}
    Helpful Answer:
"""'''
template = """
    Ti faccio una domanda alla quale vorrei che tu rispondessi, capendo il significato e trasformandolo"
    generando solamente una query SQL per un database PostgreSQL,
    basandoti sulla DDL fornita qui di seguito e il contesto in input.
    Utilizza solamente SELECT statements. Non utilizzare commenti.
    Prova sempre a dare una risposta, se proprio non puoi dare una risposta: rispondi N/A \n {question}{context} \n"""+f"{ddl}"

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)


qa = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={ "prompt": QA_CHAIN_PROMPT}
)


'''
# Run chain
self_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectordb.as_retriever(),
    document_contents= "query",
    metadata_field_info=[AttributeInfo(name="query", description="query", type="string")],
    chain_kwargs={"prompt": QA_CHAIN_PROMPT}
)
memory integration TO BE TESTED

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

'''
