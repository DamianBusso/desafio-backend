# Desafío Backend – API de Progreso de Alumnos (FastAPI)

API REST hecha con **Python + FastAPI**. Los datos se guardan en memoria (listas), no hay base de datos persistente: al reiniciar el servidor se pierden los ejercicios cargados.

## Requisitos

- Python 3.10 o superior
- pip

## Cómo correrla localmente

```bash
# 1. Clonar el repo
git clone <URL_DEL_REPO>
cd desafio-backend-py

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar el servidor
uvicorn main:app --reload
```

El servidor queda corriendo en `http://localhost:8000`.

## Datos iniciales (seed)

| id | nombre |
|----|--------|
| 1  | Juan Perez |
| 2  | Maria Gomez |
| 3  | Carlos Lopez |

## Endpoints

### `GET /alumnos`
Devuelve todos los alumnos con su promedio actual y, si corresponde, `status: "Elite"` (promedio > 90).

```bash
curl http://localhost:8000/alumnos
```

### `POST /ejercicios`
Registra el resultado de un ejercicio. Body JSON requerido: `alumno_id` (int), `ejercicio_id` (int), `score` (número).

- `score` debe estar entre 0 y 100, si no devuelve `400`.
- Si falta algún campo o el tipo es incorrecto, FastAPI devuelve `422` automáticamente (validación de Pydantic).
- Si `alumno_id` no existe, devuelve `404`.

```bash
curl -X POST http://localhost:8000/ejercicios \
  -H "Content-Type: application/json" \
  -d '{"alumno_id":1,"ejercicio_id":101,"score":95}'
```

Ejemplo de error por score fuera de rango:

```bash
curl -X POST http://localhost:8000/ejercicios \
  -H "Content-Type: application/json" \
  -d '{"alumno_id":1,"ejercicio_id":102,"score":150}'
# -> 400 Bad Request
```

### `GET /progreso/{alumno_id}`
Devuelve el promedio de un alumno puntual. Incluye `status: "Elite"` si el promedio es mayor a 90.

```bash
curl http://localhost:8000/progreso/1
```

Respuesta de ejemplo:

```json
{
  "id": 1,
  "nombre": "Juan Perez",
  "promedio": 93.5,
  "cantidadEjercicios": 2,
  "status": "Elite"
}
```

## Notas

- La validación del rango de `score` (0-100 → 400) se implementa a mano dentro del endpoint, en lugar de usar `Field(ge=0, le=100)` de Pydantic. Esto es intencional: Pydantic con esa restricción devolvería `422` en vez del `400` que pide la consigna, así que se separan las dos capas de validación (formato de datos vs. regla de negocio).
