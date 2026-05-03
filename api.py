from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List, Dict

app = FastAPI(
    title="API de Remates Judiciales",
    description="API REST para consultar registros de remates judiciales extraídos de la Judicatura.",
    version="1.0.0"
)

DB_PATH = "remates.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite retornar diccionarios en vez de tuplas
    return conn

@app.get("/", tags=["Estado"])
def read_root():
    return {"mensaje": "API de Remates Judiciales en Línea (FastAPI)"}

@app.get("/api/remates", response_model=List[Dict], tags=["Remates"])
def get_todos_remates():
    """Devuelve todos los remates almacenados en la base de datos."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM remates ORDER BY fecha DESC")
        remates = cursor.fetchall()
        conn.close()
        return [dict(ix) for ix in remates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lugares", response_model=List[str], tags=["Ubicaciones"])
def get_lugares():
    """Devuelve una lista de ubicaciones únicas disponibles."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ubicacion FROM remates WHERE ubicacion IS NOT NULL")
        lugares_raw = cursor.fetchall()
        conn.close()
        lugares = []
        for row in lugares_raw:
            lug = row[0].replace('\n', ', ').strip()
            if lug and lug not in lugares:
                lugares.append(lug)
        lugares.sort()
        return lugares
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/remates/{codigo}", response_model=Dict, tags=["Remates"])
def get_remate_por_codigo(codigo: str):
    """Devuelve los detalles de un remate específico buscando por su código."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM remates WHERE codigo = ?", (codigo,))
        remate = cursor.fetchone()
        conn.close()
        if remate:
            return dict(remate)
        else:
            raise HTTPException(status_code=404, detail="Remate no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/remates/provincia/{provincia}", response_model=List[Dict], tags=["Remates"])
def get_remates_por_provincia(provincia: str):
    """Filtra y devuelve todos los remates que correspondan a una ubicación o provincia."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # LIKE permite buscar coincidencias con seguridad. 
        # Como las opciones del dropdown convirtieron \n a ", ", reeplazamos la coma con un comodín % 
        # para que SQLite haga match correctamente con el salto de línea original (ej. LOJA\nPINDAL)
        query = "SELECT * FROM remates WHERE ubicacion LIKE ? ORDER BY fecha DESC"
        filtro_sql = '%' + provincia.upper().replace(', ', '%') + '%'
        cursor.execute(query, (filtro_sql,))
        remates = cursor.fetchall()
        conn.close()
        return [dict(ix) for ix in remates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
