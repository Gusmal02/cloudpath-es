import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import arch, exam, study, progress, admin, whatif, generate, tutor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        from pathlib import Path
        from questions.loader import load_questions_from_file
        from questions.chroma_client import embed_questions
        questions_dir = Path(settings.questions_dir)
        files = list(questions_dir.glob("*.json"))
        if files:
            all_questions = []
            for f in files:
                try:
                    all_questions.extend(load_questions_from_file(str(f)))
                except Exception as exc:
                    logger.warning("Error cargando preguntas de %s: %s", f, exc)
            if all_questions:
                embed_questions(all_questions, collection_name="questions", chroma_path=settings.chroma_path)
            else:
                logger.warning("No se cargaron preguntas — el modo examen no funcionará correctamente")
    except Exception as exc:
        logger.error("Error en lifespan al cargar preguntas: %s", exc)
    yield


app = FastAPI(title="CloudPath ES", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exam.router)
app.include_router(study.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(arch.router)
app.include_router(whatif.router)
app.include_router(generate.router)
app.include_router(tutor.router)


@app.get("/health")
def health():
    settings = get_settings()
    try:
        from pathlib import Path
        port = int(Path(settings.port_file).read_text().strip())
    except Exception:
        port = None
    return {"status": "ok", "port": port}


if __name__ == "__main__":
    import uvicorn
    from port_finder import find_free_port
    settings = get_settings()
    port = find_free_port(port_file=settings.port_file)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
