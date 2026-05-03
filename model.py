from pydantic import BaseModel

class Task  (BaseModel): 
    title:str 
    done:bool=False 

class StoredTask  (BaseModel):
    id: int
    title:str 
    done:bool=False 

class User(BaseModel):
    name:str 
    email: str
    password: str
class StoredUser(BaseModel):
    id: int
    name:str 
    email: str
    password: str
class Userlogin(BaseModel): 
    email: str
    password: str

