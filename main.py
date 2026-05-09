from fastapi import FastAPI,HTTPException
from schemas import TaskCreate,TaskResponse,UserCreate,UserResponse,Userlogin
from passlib.context import CryptContext
from dotenv import load_dotenv 
import os 
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
# from fastapi import Depends 
from database import engine 
from models import Base 
from database import get_db
from models import User,Task 
from sqlalchemy.orm import Session  
from fastapi import Depends

Base.metadata.create_all(bind=engine) 

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

@app.get("/task")
def get_task(current_user: str=Depends(get_current_user),db=Depends(get_db)):
    # Step 1 — find the user by email to get their id
    existing_user=db.query(User).filter(User.email==current_user).first()

    # Step 2 — filter tasks by that id 
    filtered_task=db.query(Task).filter(Task.owner_id==existing_user.id).all()

    return {'hello task ': filtered_task}

@app.post("/tasks") 
def create_task(task: TaskCreate, current_user: str=Depends(get_current_user),db=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==current_user).first() 

    new_task=Task(
        title=task.title,
        description=task.description,
        done=task.done,
        owner_id=existing_user.id
    ) 
    db.add(new_task)
    db.commit() 
    db.refresh(new_task) # without this new_task will reurn empty body 
    return new_task

@app.put("/tasks/{id}")
def update_task(id:int,task:TaskCreate, current_user: str=Depends(get_current_user),db=Depends(get_db)):
    
    existing_user= db.query(User).filter(User.email==current_user).first()
    existing_user_task=db.query(Task).filter(Task.id==id).first()  
    if not existing_user_task:
        raise  HTTPException(status_code=404,detail= f" this task at id: {id} not found")
    if existing_user.id != existing_user_task.owner_id:
        raise HTTPException(status_code=403, detail="not authorized to update this task") 
    
    existing_user_task.title=task.title
    existing_user_task.description=task.description
    existing_user_task.done=task.done 
    db.commit()  
    db.refresh(existing_user_task) 
    return {"message": f" task at id: {id} updated successfully"} 
        
                
@app.delete("/tasks/{id}") 
def delete_post(id:int, current_user: str=Depends(get_current_user),db=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==current_user).first()
    existing_user_task=db.query(Task).filter(Task.id==id).first()
    if not existing_user_task:
        raise HTTPException(status_code=404, detail="task not found") 
    if existing_user_task.owner_id != existing_user.id:
        raise HTTPException(status_code=403,detail="you are not authorized user to delete this task")

    db.delete(existing_user_task)
    db.commit() 
    return {"message": f"task {id} deleted successfully"}


# add post or register method for user ............................... 
pwd_context=CryptContext(schemes=["bcrypt"]) 

@app.post("/user_register")
def register(user_data:UserCreate,db=Depends(get_db)): 
    existing_user=db.query(User).filter(user_data.email==User.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail= "email already exit" ) 

    db_user=User(
        name=user_data.name,
        email=user_data.email, 
        password=pwd_context.hash(user_data.password[:72] ) 
    )
    db.add(db_user)   
    db.commit() 
    return {'message ': f'{user_data.name} your registration is successfull.'}

@app.post('/user_login')
def login(form_data: OAuth2PasswordRequestForm=Depends(), db=Depends(get_db)):  
    existing_user= db.query(User).filter(User.email==form_data.username).first()
    
    if not existing_user:
        raise HTTPException(status_code=400, detail= "incorrect email or password") 
    if not pwd_context.verify(form_data.password, existing_user.password):
        raise HTTPException(status_code=400, detail="incorrect email or password") 
    
    token=create_token(existing_user.email)  
    return {"access_token": token, "token_type": "bearer"} 
