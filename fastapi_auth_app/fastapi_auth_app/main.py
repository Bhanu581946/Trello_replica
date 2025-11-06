from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routes import users, boards, tasks

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trello Clone App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(boards.router)
app.include_router(tasks.router)

# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
