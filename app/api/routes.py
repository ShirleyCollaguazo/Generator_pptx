from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from app.services.generator import run_pipeline

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/generate")
async def generate(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    job_id = str(uuid.uuid4())

    tmp_dir = Path("tmp")
    out_dir = Path("outputs")

    tmp_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    pdf_path = tmp_dir / f"{job_id}.pdf"
    pptx_path = out_dir / f"{job_id}.pptx"

    # Guardar PDF
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Ejecutar pipeline
    try:
        run_pipeline(pdf_path=pdf_path, output_path=pptx_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Devolver PPTX
    return FileResponse(
        path=pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="slides_generadas.pptx"
    )
