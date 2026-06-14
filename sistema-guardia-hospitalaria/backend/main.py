from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401 — registers all models so create_all includes all tables
from routers.paciente import router as paciente_router
from routers.medico import router as medico_router
from routers.ingreso_guardia import router as ingreso_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(ingreso_router)


@app.get("/")
def root():
    return {"status": "ok"}
