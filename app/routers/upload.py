import io
import re
import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import QuizQuestion

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

REQUIRED_COLUMNS = [
    "course_num",
    "chapter",
    "question",
    "choice_a",
    "choice_b",
    "choice_c",
    "choice_d",
    "choice_e",
    "correct_answer",
    "explaination",
]

REQUIRED_FIELDS = [
    "course_num",
    "chapter",
    "question",
    "choice_a",
    "choice_b",
    "choice_c",
    "choice_d",
]

ANSWER_NUMBER_MAP = {
    "1": "A",
    "2": "B",
    "3": "C",
    "4": "D",
    "5": "E",
}

def parse_course_num(value: object) -> int | None:
    if pd.isna(value):
        return None
        
    raw = str(value).strip()
    if not raw:
        return None
        
    if not raw.isdigit():
        return None
        
    parsed = int(raw)
    if parsed < 0 or parsed > 32767:
        return None
        
    return parsed

def normalize_correct_answer(value: object) -> str | None:
    if pd.isna(value):
        return None
        
    raw = str(value).strip().upper()
    if not raw:
        return None
        
    match = re.search(r"[A-E1-5]", raw)
    if not match:
        return None
        
    token = match.group(0)
    if token in {"A", "B", "C", "D", "E"}:
        return token
        
    return ANSWER_NUMBER_MAP.get(token)

@router.post("/upload-csv")
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "error": "Please upload a CSV file."
            },
            status_code=400
        )
        
    content = await file.read()
    
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "error": f"Unable to parse CSV: {str(e)}"
            },
            status_code=400
        )
        
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "error": f"Missing columns: {', '.join(missing)}"
            },
            status_code=400
        )
        
    inserted = 0
    skipped_missing_required = 0
    skipped_invalid_answer = 0
    skipped_invalid_course = 0
    
    for _, row in df.iterrows():
        missing_required = [
            field for field in REQUIRED_FIELDS
            if pd.isna(row[field]) or not str(row[field]).strip()
        ]
        if missing_required:
            skipped_missing_required += 1
            continue
            
        course_num = parse_course_num(row["course_num"])
        if course_num is None:
            skipped_invalid_course += 1
            continue
            
        correct_answer = normalize_correct_answer(row["correct_answer"])
        if not correct_answer:
            skipped_invalid_answer += 1
            continue
            
        item = QuizQuestion(
            course_num=course_num,
            chapter=str(row["chapter"]).strip(),
            question=str(row["question"]).strip(),
            choice_a=str(row["choice_a"]).strip(),
            choice_b=str(row["choice_b"]).strip(),
            choice_c=str(row["choice_c"]).strip(),
            choice_d=str(row["choice_d"]).strip(),
            choice_e="" if pd.isna(row["choice_e"]) else str(row["choice_e"]).strip(),
            correct_answer=correct_answer,
            explaination="" if pd.isna(row["explaination"]) else str(row["explaination"]).strip()
        )
        
        db.add(item)
        inserted += 1

    db.commit()

    skipped_total = (
        skipped_missing_required
        + skipped_invalid_answer
        + skipped_invalid_course
    )

    success_message = (
        f"CSV uploaded successfully. Inserted {inserted} question(s)."
    )

    if skipped_total:
        success_message += (
            f" Skipped {skipped_total} row(s) "
            f"(missing required fields: {skipped_missing_required}, "
            f"invalid course_num: {skipped_invalid_course}, "
            f"invalid correct_answer: {skipped_invalid_answer})."
        )

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "success": success_message
        }
    )