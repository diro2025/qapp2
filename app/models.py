from sqlalchemy import Column, Integer, SmallInteger, String, Text
from app.db import Base

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    course_num = Column(SmallInteger, index=True, nullable=False)
    chapter = Column(String(100), index=True, nullable=False)
    question = Column(Text, nullable=False)
    choice_a = Column(Text, nullable=False)
    choice_b = Column(Text, nullable=False)
    choice_c = Column(Text, nullable=False)
    choice_d = Column(Text, nullable=False)
    choice_e = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explaination = Column(Text, nullable=True)