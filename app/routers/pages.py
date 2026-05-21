from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import QuizQuestion

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    pairs = db.execute(
        select(QuizQuestion.course_num, QuizQuestion.chapter)
        .distinct()
        .order_by(QuizQuestion.course_num, QuizQuestion.chapter)
    ).all()

    courses: dict[int, list[str]] = {}
    for course_num, chapter in pairs:
        courses.setdefault(course_num, []).append(chapter)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "courses": courses
        }
    )

@router.get("/quiz")
def quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})

@router.get("/upload")
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})