from pathlib import Path
import tempfile, zipfile
import geopandas as gpd
import pandas as pd

def read_file(path):
    if path.suffix.lower() == ".kml":
        try: return gpd.read_file(path, driver="KML")
        except Exception: return gpd.read_file(path)
    if path.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory() as d:
            out = Path(d).resolve()
            with zipfile.ZipFile(path) as z:
                for m in z.infolist():
                    target = (out/m.filename).resolve()
                    if not str(target).startswith(str(out)): raise ValueError("Unsafe ZIP archive.")
                z.extractall(out)
            shp = next(out.rglob("*.shp"), None)
            if shp is None: raise ValueError("ZIP does not contain a .shp Shapefile.")
            return gpd.read_file(shp)
    raise ValueError("Unsupported file type.")

def clean(v):
    if pd.isna(v): return None
    try: return v.item()
    except Exception: return v

def process_geospatial_file(path):
    gdf = read_file(path)
    crs = str(gdf.crs) if gdf.crs else None
    projected = gdf
    if gdf.crs and gdf.crs.is_geographic:
        projected_crs = gdf.estimate_utm_crs()
        if not projected_crs:
            raise ValueError("Could not determine a projected CRS.")
        projected = gdf.to_crs(projected_crs)

    results = []
    for idx, geom in gdf.geometry.items():
        pgeom = projected.geometry.loc[idx]
        typ = geom.geom_type if geom is not None else "Unknown"
        props = {c:clean(gdf.loc[idx,c]) for c in gdf.columns if c != gdf.geometry.name}
        item = {"feature_id":int(idx) if isinstance(idx,int) else str(idx),
                "geometry_type":typ,
                "geometry":geom.__geo_interface__ if geom is not None else None,
                "crs":crs,"properties":props,"measurement":None,"measurement_unit":None}
        if geom is not None and not geom.is_empty:
            if typ in ("Polygon","MultiPolygon"):
                item["measurement"]=float(pgeom.area); item["measurement_unit"]="square_metres"
            elif typ in ("LineString","MultiLineString"):
                item["measurement"]=float(pgeom.length); item["measurement_unit"]="metres"
        results.append(item)
    return {"feature_count":len(gdf),"crs":crs,"measurements":results}
