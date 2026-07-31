import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas import TranslationOptions
from app.services.translator import PptTranslatorService

app = FastAPI(title="PPT Translator BS Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/translate/pptx")
async def translate_pptx(
    file: UploadFile = File(...),
    options_json: str = Form(...),
):
    suffix = Path(file.filename or "input.pptx").suffix.lower()
    if suffix != ".pptx":
        raise HTTPException(status_code=400, detail="Only .pptx files are supported.")

    try:
        options = TranslationOptions.model_validate(json.loads(options_json))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid options_json: {exc}") from exc

    with tempfile.TemporaryDirectory(prefix="ppt-translator-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "input.pptx"
        output_path = tmp_path / "output_translated.pptx"

        raw = await file.read()
        input_path.write_bytes(raw)

        try:
            service = PptTranslatorService(options)
            service.translate_pptx(input_path=input_path, output_path=output_path)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Translation failed: {exc}") from exc

        download_name = f"{Path(file.filename or 'input').stem}_translated.pptx"
        return FileResponse(
            path=str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=download_name,
        )

