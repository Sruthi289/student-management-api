from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String,ForeignKey,func



load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    db = SessionLocal()
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/")
def home():
    return {"message": "Hello, world"}

@app.get("/about")
def about():
    return {"message" : "FAST API demonstration"}

@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"db_connected": True, "result": result.fetchone()[0]}
    
@app.post("/students")
def add_student(first_name: str, last_name: str, email: str,user=Depends(get_current_user)):
    db = SessionLocal()
    new_student = Student(first_name=first_name, last_name=last_name, email=email)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    db.close()
    return {"id": new_student.id, "first_name": new_student.first_name}

@app.get("/students")
def get_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return students

@app.get("/students/{id}")
def get_student(id: int):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == id).first()
    db.close()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.delete("/students/{id}")
def delete_student(id: int,user=Depends(get_current_user)):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == id).first()
    if student is None:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    db.close()
    return {"message": "Student deleted"}

@app.put("/students/{id}")
def update_student(id: int, first_name: str, last_name: str, email: str,user=Depends(get_current_user)):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == id).first()
    if student is None:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")
    student.first_name = first_name
    student.last_name = last_name
    student.email = email
    db.commit()
    db.refresh(student)
    db.close()
    return student

@app.post("/courses")
def add_course(title: str, student_id: int,user=Depends(get_current_user)):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")
    new_course = Course(title=title, student_id=student_id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    db.close()
    return new_course


@app.get("/students/{id}/courses")
def get_student_courses(id: int):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == id).first()
    if student is None:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")
    courses = db.query(Course).filter(Course.student_id == id).all()
    db.close()
    return courses

@app.get("/reports/courses-per-student")
def courses_per_student():
    db = SessionLocal()
    rows = (
        db.query(Student.id, Student.first_name, Student.last_name, func.count(Course.id))
        .outerjoin(Course, Course.student_id == Student.id)
        .group_by(Student.id, Student.first_name, Student.last_name)
        .all()
    )
    db.close()
    return [
        {"id": r[0], "name": f"{r[1]} {r[2]}", "course_count": r[3]}
        for r in rows
    ]
@app.post("/signup")
def signup(user: UserCreate):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"id": new_user.id, "email": new_user.email}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.email == form.username).first()
    db.close()
    if user is None or not bcrypt.checkpw(form.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    token = jwt.encode({"sub": user.email, "exp": expire}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}