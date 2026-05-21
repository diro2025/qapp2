import random
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import QuizQuestion

router = APIRouter()

@router.get("/questions")
def get_questions(
    chapters: list[str] = Query(default=[]),
    course_nums: list[int] = Query(default=[]),
    randomize: bool = False,
    db: Session = Depends(get_db)
):
    stmt = select(QuizQuestion)

    if course_nums:
        stmt = stmt.where(QuizQuestion.course_num.in_(course_nums))
        
    if chapters:
        stmt = stmt.where(QuizQuestion.chapter.in_(chapters))
        
    questions = db.execute(stmt).scalars().all()

    results = []
    for q in questions:
        results.append({
            "id": q.id,
            "course_num": q.course_num,
            "chapter": q.chapter,
            "question": q.question,
            "choices": {
                "A": q.choice_a,
                "B": q.choice_b,
                "C": q.choice_c,
                "D": q.choice_d,
                "E": q.choice_e,
            },
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "explaination": q.explaination,
        })

    if randomize:
        random.shuffle(results)

    return results