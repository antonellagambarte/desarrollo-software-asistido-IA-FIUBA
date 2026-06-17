from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401 — registers all models so create_all includes all tables
from routers.paciente import router as paciente_router
from routers.medico import router as medico_router
from routers.ingreso_guardia import router as ingreso_router
from routers.auth import router as auth_router
from ws.connection_manager import manager

Base.metadata.create_all(bind=engine)

# Migración: agregar columna especialidad_requerida si no existe
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(
        __import__('sqlalchemy').text("PRAGMA table_info(ingresos_guardia)")
    )]
    if 'especialidad_requerida' not in cols:
        conn.execute(__import__('sqlalchemy').text(
            "ALTER TABLE ingresos_guardia ADD COLUMN especialidad_requerida TEXT"
        ))
        conn.commit()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(ingreso_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
