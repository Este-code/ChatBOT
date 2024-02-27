# to be launched only once
import chromadb

persist_directory = "./chroma"

chroma_client = chromadb.PersistentClient(persist_directory)
collection = chroma_client.get_or_create_collection(name="chatbot")