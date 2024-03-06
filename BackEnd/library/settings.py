from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from library.common import get_config_value
from library.ddl import ddl
import library.CustomVectorDB as CVDB

load_dotenv(find_dotenv()) # reads local .env file
dati_connessione = get_config_value("dati_connessione")
engine = create_engine(dati_connessione)

path = "vectordb"
vectordb = CVDB.CustomVectorDB(path)

# Build prompt
template = """
    Ti faccio una domanda alla quale vorrei che tu rispondessi, capendo il significato e trasformandolo"
    generando solamente una query SQL per un database PostgreSQL,
    basandoti sulla DDL fornita qui di seguito e il contesto in input.
    Utilizza solamente SELECT statements. Non utilizzare commenti.
    Qui ha inizio la DDL \n"""+f"{ddl}"+"""\n Qui ha fine la DDL
    Prova sempre a dare una risposta, se proprio non puoi dare una risposta: rispondi N/A
    {context}
    Question: {question}
    Helpful Answer:
"""

