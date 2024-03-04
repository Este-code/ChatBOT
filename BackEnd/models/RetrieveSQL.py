from pydantic import BaseModel

class RetrieveSQL(BaseModel):
    query: str