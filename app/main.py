from fastapi import FastAPI, File, HTTPException, UploadFile
from .processor import process_geospatial_file
from uuid import uuid4
from pathlib import Path
import tempfile
import shutil

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0"
)

FILES = {}


@app.get("/")
def root():
    return {
        "name": "Geospatial File Measurement API",
        "status": "running",
        "docs": "/docs"
    }


@app.post("/api/files/", status_code=201)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    name = file.filename.lower()

    if not (name.endswith(".kml") or name.endswith(".zip")):
        raise HTTPException(
            status_code=400,
            detail="Only .kml or .zip files are supported."
        )

    file_id = str(uuid4())[:12]

    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / file.filename

        with path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        try:
            result = process_geospatial_file(path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to process file: {e}"
            )

    result.update(
        id=file_id,
        filename=file.filename,
        status="COMPLETED"
    )

    FILES[file_id] = result

    return result


@app.get("/api/files/{file_id}/")
def file_info(file_id: str):
    result = FILES.get(file_id)

    if not result:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        key: result[key]
        for key in ["id", "filename", "feature_count", "crs", "status"]
    }


@app.get("/api/files/{file_id}/measurements/")
def measurements(file_id: str):
    result = FILES.get(file_id)

    if not result:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        "id": result["id"],
        "filename": result["filename"],
        "measurements": result["measurements"]
    }