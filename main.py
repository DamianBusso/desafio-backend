from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="API de Progreso de Alumnos")

# ============================================
# "BASE DE DATOS" EN MEMORIA
# Se reinicia cada vez que se reinicia el servidor.
# ============================================

alumnos = [
    {"id": 1, "nombre": "Juan Perez"},
    {"id": 2, "nombre": "Maria Gomez"},
    {"id": 3, "nombre": "Carlos Lopez"},
]

#se van acumulando los resultados que llegan por POST /ejercicios{"alumno_id": int, "ejercicio_id": int, "score": float}
ejercicios = []

# ============================================
# MODELO DE ENTRADA (Pydantic)
# a propósito NO uso Field(ge=0, le=100) acá, para que score sea numérico.
# la haga Pydantic, pero el rango 0-100 lo valido a mano para contrlar el código de error 400.
# ============================================

class EjercicioInput(BaseModel):
    alumno_id: int
    ejercicio_id: int
    score: float

def calcular_promedio(alumno_id: int) -> tuple[Optional[float], int]:
    resultados = [e for e in ejercicios if e["alumno_id"] == alumno_id]

    if not resultados:
        return None, 0

    suma = sum(e["score"] for e in resultados)
    promedio = suma / len(resultados)
    return promedio, len(resultados)


def construir_estado_alumno(alumno: dict) -> dict:
    promedio, cantidad = calcular_promedio(alumno["id"])

    estado = {
        "id": alumno["id"],
        "nombre": alumno["nombre"],
        "promedio": round(promedio, 2) if promedio is not None else None,
        "cantidadEjercicios": cantidad,
    }

    # Regla de negocio: promedio > 90 => status "Elite"
    if promedio is not None and promedio > 90:
        estado["status"] = "Elite"

    return estado


def buscar_alumno_por_id(alumno_id: int) -> Optional[dict]:
    return next((a for a in alumnos if a["id"] == alumno_id), None)


# ============================================
# ENDPOINTS
# ============================================

@app.get("/alumnos")
def obtener_alumnos():
    """Devuelve la lista de alumnos con su estado de progreso."""
    return [construir_estado_alumno(a) for a in alumnos]


@app.post("/ejercicios", status_code=201)
def registrar_ejercicio(payload: EjercicioInput):
    """Registra el resultado de un ejercicio para un alumno."""

    #score debe estar entre 0 y 100
    if payload.score < 0 or payload.score > 100:
        raise HTTPException(status_code=400, detail="El score debe estar entre 0 y 100.")

    # Validación de que el alumno exista
    alumno = buscar_alumno_por_id(payload.alumno_id)
    if alumno is None:
        raise HTTPException(
            status_code=404, detail=f"No existe un alumno con id {payload.alumno_id}."
        )

    nuevo_registro = {
        "alumno_id": payload.alumno_id,
        "ejercicio_id": payload.ejercicio_id,
        "score": payload.score,
    }
    ejercicios.append(nuevo_registro)

    return {"mensaje": "Ejercicio registrado correctamente.", "registro": nuevo_registro}


@app.get("/progreso/{alumno_id}")
def obtener_progreso(alumno_id: int):
    """Calcula y devuelve el promedio de un alumno específico."""
    alumno = buscar_alumno_por_id(alumno_id)
    if alumno is None:
        raise HTTPException(status_code=404, detail=f"No existe un alumno con id {alumno_id}.")

    return construir_estado_alumno(alumno)
