from pydantic import BaseModel

class TaskCreate  (BaseModel): 
    title:str 
    description:str 
    done:bool=False 

class TaskResponse  (BaseModel):
    id: int 
    title:str 
    description:str
    done:bool=False
    owner_it:int  

class UserCreate(BaseModel):
    name:str 
    email: str
    password: str
class UserResponse(BaseModel):
    id: int
    name:str 
    email: str

class Userlogin(BaseModel): 
    email: str
    password: str 