import logging
import urllib.parse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine, settings
from app.routers import pages, api_quiz, upload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qapp")

def redact_db_url(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(url)
        if not parsed.password:
            return url
        netloc = parsed.netloc.replace(f":{parsed.password}", ":***")
        return urllib.parse.urlunsplit(
            (parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment)
        )
    except Exception:
        return "<unparseable database_url>"
    
logger.info("Database URL: %s", redact_db_url(settings.database_url))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz App")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(api_quiz.router, prefix="/api")
app.include_router(upload.router)