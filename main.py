from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from passlib.context import CryptContext

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["TrafficApp"]
users_collection = db["user_info"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    address: str = Field(..., min_length=1)
    phone: str = Field(..., pattern="^\\+?[0-9]{7,15}$", description="Valid phone number with 7-15 digits")
    email: EmailStr
    id_type: str = Field(..., description="ID type must be AADHAR or Driving License")
    id_number: str = Field(..., min_length=1)

class UserLogin(BaseModel):
    username: str
    password: str

app = FastAPI()

@app.post("/register/", status_code=201)
def register_user(user: UserCreate):
    if user.id_type not in ["AADHAR", "Driving License"]:
        raise HTTPException(status_code=400, detail="ID type must be 'AADHAR' or 'Driving License'")

    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = users_collection.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(user.password)

    new_user = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "password": hashed_password,
        "address": user.address,
        "phone": user.phone,
        "email": user.email,
        "id_type": user.id_type,
        "id_number": user.id_number
    }

    result = users_collection.insert_one(new_user)

    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@app.post("/login/")
def login_user(user: UserLogin):
    existing_user = users_collection.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}