from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
import models
from sqlalchemy.orm import relationship
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta

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

# Your own secret key, used to sign the JWTs
SECRET_KEY = "150903"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to create a new access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to decode and verify the token
def decode_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

# OAuth2PasswordBearer is a class for creating an OAuth2 dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        return payload
    except JWTError:
        raise credentials_exception

@app.post("/signup/")
async def signup(signup: SignUp, db: Session = Depends(get_db)):
    # Check if username already exists
    user_exists = db.query(models.User).filter(models.User.username == signup.username).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Hash the password before storing it
    hashed_password = password_hashing.hash(signup.password)
    
    # Create new user
    new_user = models.User(username=signup.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not password_hashing.verify(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Create a new access token
    access_token = create_access_token(data={"sub": form_data.username})
    return {"message": "Login successfully", "access_token": access_token, "token_type": "bearer"}

@app.post("/posts/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("Current User:", current_user)  # Add this line to check the content of current_user

    # Use the authenticated user to create and save the post
    try:
        user_id = int(current_user['sub'])
    except KeyError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_post = models.Post(**post.dict(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.get("/users/", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get("/recent_posts/", response_model=list[PostResponse])
async def list_recent_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return posts
