# to be launched only once
import chromadb
from settings import persist_direcotry

chroma_client = chromadb.PersistentClient(persist_direcotry)
collection = chroma_client.get_or_create_collection(name="chatbot")