import random
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import QuizQuestion

router = APIRouter()

@router.get("/questions")