from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import models
from sqlalchemy.orm import relationship 
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
models.User.posts = relationship("Post", back_populates="user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PostCreate(BaseModel):
    text: str

class PostResponse(BaseModel):
    id: int
    text: str
    user_id: int
    created_at: datetime

class SignUp(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# Security setup
SECRET_KEY = "your-secret-key"

# Password hashing
password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash password
def hash_password(password):
    return password_hashing.hash(password)

@app.post("/signup/")
async def signup(signup: SignUp, db: Session = Depends(get_db)):
    # Check if username already exists
    user_exists = db.query(models.User).filter(models.User.username == signup.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password before storing it
    hashed_password = hash_password(signup.password)
    
    # Create new user
    new_user = models.User(username=signup.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login/")
async def login(signup: SignUp, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == signup.username).first()
    if not user or not password_hashing.verify(signup.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful"}

#crate post
@app.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, username: str, db: Session = Depends(get_db)):
   # Fetch the user based on the provided username
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Create and save the post
    db_post = models.Post(**post.dict(), user_id=user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post

@app.get("/posts/")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# List all users
@app.get("/users/", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/recent_posts/", response_model=list[PostResponse])
async def list_recent_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return posts