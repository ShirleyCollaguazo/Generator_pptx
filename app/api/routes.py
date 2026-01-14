from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid

from app.services.generator import run_pipeline

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate")
async def generate(payload: dict):
    """
    Recibe TEXTO PLANO como entrada y devuelve un PPTX generado.
    Espera un JSON con la clave:
    {
        "text": "contenido académico..."
    }
    """

    input_text = payload.get("text")

    if not input_text or not isinstance(input_text, str):
        raise HTTPException(
            status_code=400,
            detail="Field 'text' is required and must be a string"
        )

    job_id = str(uuid.uuid4())

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    pptx_path = out_dir / f"{job_id}.pptx"

    # Ejecutar pipeline
    try:
        run_pipeline(
            input_text=input_text,
            output_path=pptx_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Devolver PPTX
    return FileResponse(
        path=pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="slides_generadas.pptx"
    )

