from fastapi import FastAPI,HTTPException
from model import Task,StoredTask,User,StoredUser,Userlogin
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from fastapi import Depends

load_dotenv() 
secret_key=os.getenv("SECRET_KEY")
algorithm=os.getenv("ALGORITHM")
Access_token_expiry_minutes= int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) 


def create_token(email:str):
    expiry=datetime.utcnow() + timedelta(minutes=Access_token_expiry_minutes)  
    payload={
        "sub":email, 
        "exp":expiry
    } 
    token=jwt.encode(payload,secret_key , algorithm=algorithm) 
    return token 

# create a fun to check token is valid and current use is valid user
oath2_scheme=OAuth2PasswordBearer(tokenUrl="user_login") 
def get_current_user(token: str = Depends(oath2_scheme)):
    try:
        print("TOKEN RECEIVED:", token)
        print("SECRET KEY:", secret_key)
        print("ALGORITHM:", algorithm)
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email = payload.get("sub")
        return email
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=401, detail="invalid or expired token")
    
app=FastAPI() 

task_db=[] 
user_db=[] 
# @app.get("/health")
# def health_check():
#     return {"status": " OK"} 

# @app.get("/hello/{name}")
# def say_hello(name:str):  
#     return {f"hello {name}"}

# @app.get("/user/{id}") 
# def user_id(id:int):
#     return {"id ": id} 

@app.get("/task")
def get_task(current_user: str=Depends(get_current_user)):
    return task_db  

@app.post("/tasks")
def create_task(task: Task, current_user: str=Depends(get_current_user)):
    new_id = len(task_db) + 1       # generate id
    stored = StoredTask(            # create StoredTask with all 3 fields
        id = new_id,
        title = task.title,
        done = task.done 
    ) 
    task_db.append(stored)          # append the StoredTask
    return stored    

@app.put("/tasks/{id}")
def update_task(id:int,task:Task, current_user: str=Depends(get_current_user)):
    for item in task_db:
        if item.id==id:
            item.title=task.title
            item.done=task.done 
            return {"message": f" task at id: {id} updated successfully"} 
        
    raise  HTTPException(status_code=404,detail= f" this item at id: {id} not exit")
                
@app.delete("/tasks/{id}") 
def delete_post(id:int, current_user: str=Depends(get_current_user)):
    for item in task_db:
        if item.id==id: 
            task_db.remove(item) 
            return {"message": f" task at id: {id} deleted successfully"} 
        
    raise HTTPException(status_code=404, detail=f"this item of id: {id} doesn't exit") 

# add post or register method for user ............................... 
pwd_context=CryptContext(schemes=["bcrypt"]) 

@app.post("/user_register")
def register(user_data:User):
    for item in user_db:
        if item.email == user_data.email:
            raise HTTPException(status_code=400, detail= "email already exit" ) 

    db_len= len(user_db) + 1 
    stored_Data= StoredUser( 
       id=db_len,
       name= user_data.name,
       email=user_data.email,
       password = pwd_context.hash(user_data.password[:72])
    )  
    user_db.append(stored_Data)  
    return {'message ': f'{user_data.name} your registration is successfull.'}

@app.post('/user_login')
def login(form_data: OAuth2PasswordRequestForm=Depends()): 
    for item in user_db:
        if item.email== form_data.username and pwd_context.verify(form_data.password,item.password):
            token=create_token(form_data.username)
            return {"access_token": token, "token_type": "bearer"} 
    raise HTTPException(status_code=400, detail= "incorrect email or password") 
