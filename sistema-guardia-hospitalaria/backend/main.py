from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401 — registers all models so create_all includes all tables
from routers.paciente import router as paciente_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)


@app.get("/")
def root():
    return {"status": "ok"}
