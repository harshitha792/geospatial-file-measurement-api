# Geospatial File Measurement API

FastAPI backend for uploading KML files or ZIP archives containing Shapefiles, extracting features, handling CRS, and calculating measurements.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Endpoints
- POST `/api/files/` — upload `.kml` or `.zip` Shapefile
- GET `/api/files/{id}/` — file information
- GET `/api/files/{id}/measurements/` — feature measurements

## Measurement
Polygon/MultiPolygon: area in square metres.
LineString/MultiLineString: length in metres.
Point/MultiPoint: no measurement.

If the source CRS is geographic, such as EPSG:4326, geometry is transformed to an estimated local UTM projected CRS before area/length calculation.

## Architecture
Client → FastAPI → File validation → GeoPandas/GDAL → Feature extraction → CRS transformation → Measurement engine → API response.

## Test
```bash
pytest
```

## Future scope
PostgreSQL/PostGIS persistence, authentication, background jobs, cloud storage, file limits, logging and monitoring.
