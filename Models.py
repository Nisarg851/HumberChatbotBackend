from pydantic import BaseModel

class PromptModel(BaseModel):
    user_role: str
    query: str

class QueryModel(BaseModel):
    user_role: str
    query: str

class MetaDataModel(BaseModel):
    url: str