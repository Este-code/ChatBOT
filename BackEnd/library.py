import re
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import settings as sts
from langchain.vectorstores import Chroma

def retrieve_answer_using_base_prompt(question):
    result = sts.qa({"query":question})
    #result["source_documents"][0]
    return result["result"]

def retrieve_answer(question):
    compressed_docs = sts.compressor_retreiver.get_relevant_documents(question)
    return compressed_docs

def store_document(file):
    splitted_document = split_pdf_document(file)
    vectordb = Chroma.from_documents(
        documents = splitted_document,
        embedding = sts.embedding,
        persist_directory = sts.persist_directory
    )
    vectordb.persist()

def split_pdf_document(file):
    loader = PyPDFLoader(file) # loading the pdf document
    chunk_size_, chunk_overlap_ = initialize_chunk_parameters(loader.load().page_content)
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_,
        chunk_overlap=chunk_overlap_,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""]
    )
    splits = r_splitter.split_documents(loader.load())
    return splits

def calculate_average_word_length(text):
    words = text.split()
    total_length = sum(len(word) for word in words)
    return total_length / len(words)

def calculate_word_density(text):
    words = text.split()
    return len(words) / len(text)

def initialize_chunk_parameters(text):
    average_word_length = calculate_average_word_length(text)
    word_density = calculate_word_density(text)

    if word_density > 0.5:
        # high density
        chunk_size = int(average_word_length * 8) # Adjust multiplier
        overlap = int(average_word_length * 0.4) # Adjust multiplier       
    else:
        # low to moderate density
        chunk_size = int(average_word_length * 10) # Adjust multiplier
        overlap = int(average_word_length * 0.2) # Adjust multiplier

    return chunk_size, overlap

def clean_text(text):
        # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters except alphanumeric and space
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    return text