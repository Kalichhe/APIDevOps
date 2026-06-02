from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoMessageCreate,
    EmpleadoMessagePut,
    EmpleadoMessageRead,
    EmpleadoMessageUpdate,
    EmpleadoPut,
    EmpleadoUpdate,
)
from app.crud import crud_empleado
from app.models.registro_labor import RegistroLabor

router = APIRouter()


def _responder_data_json(empleado, fallback: dict | None = None):
    # Ensure required response keys are always present even for legacy rows.
    base_data = {}
    if empleado is not None:
        if getattr(empleado, "cedula", None) is not None:
            base_data["cedula"] = empleado.cedula
        if getattr(empleado, "nombre", None) is not None:
            base_data["nombre"] = empleado.nombre
        if getattr(empleado, "rol", None) is not None:
            base_data["rol"] = empleado.rol

    payload = {}
    if empleado is not None and isinstance(getattr(empleado, "data_json", None), dict):
        payload = empleado.data_json
    elif isinstance(fallback, dict):
        payload = fallback

    if not payload:
        return base_data

    normalized = dict(payload)
    for key, value in base_data.items():
        normalized.setdefault(key, value)
    return normalized


# Funcion para crear a un Empleado
@router.post("/", status_code=201, response_model=EmpleadoMessageRead)
def crear_empleado(mensaje: EmpleadoMessageCreate, db: Session = Depends(get_db)):

    # 1. Obtenemos el payload completo directamente del modelo
    # Nota: model.model_dump() mantiene la estructura tal como llegó
    payload = mensaje.model_dump(by_alias=True, exclude_none=False)

    # 2. Validamos la estructura esperada
    try:
        cedula = payload.get("cedula")
        nombre = payload.get("nombre")
        rol = payload.get("rol")

        if (
            cedula is None
            or nombre is None
            or rol is None
            or str(nombre).strip() == ""
            or str(rol).strip() == ""
        ):
            raise ValueError("Faltan campos: cedula, nombre o rol")
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=400, detail=f"Estructura JSON inválida: {str(e)}"
        )

    # 3. Verificamos si ya existe el empleado
    db_empleado = crud_empleado.get_empleado(db, cedula)
    if db_empleado:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un empleado con la cédula {cedula}",
        )

    # 4. Creamos el empleado en la BD guardando el JSON completo
    nuevo_empleado = crud_empleado.create_empleado(
        db,
        EmpleadoCreate(
            cedula=cedula,
            nombre=nombre,
            rol=rol,
        ),
        data_json=payload,
    )

    # 5. Devolvemos solo el contenido guardado en data_json
    return _responder_data_json(nuevo_empleado, payload)


# Funcion para buscar empleados
@router.get("/", response_model=list[EmpleadoMessageRead])
def listar_empleados(db: Session = Depends(get_db)):
    empleados = crud_empleado.get_empleados(db)
    return [
        _responder_data_json(
            empleado,
            {"cedula": empleado.cedula, "nombre": empleado.nombre, "rol": empleado.rol},
        )
        for empleado in empleados
    ]


# Funcion para buscar a un empleado
@router.get("/{empleado_cedula}", response_model=EmpleadoMessageRead)
def obtener_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not empleado:
        raise HTTPException(
            status_code=404,
            detail=f"Empleado con cédula {empleado_cedula} no encontrado.",
        )
    return _responder_data_json(
        empleado,
        {"cedula": empleado.cedula, "nombre": empleado.nombre, "rol": empleado.rol},
    )


# Funcion para poder modificar a un empleado usando Patch (modificada)
@router.patch("/{empleado_cedula}", status_code=200)
def actualizar_empleado(
    empleado_cedula: int, mensaje: EmpleadoMessageUpdate, db: Session = Depends(get_db)
):
    # 1. Obtenemos el payload completo
    payload = mensaje.model_dump(by_alias=True, exclude_none=False)
    payload = {k: v for k, v in payload.items() if v is not None}

    # 2. Verificamos si existe el empleado
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede actualizar: Empleado no encontrado."
        )

    # 3. Extraemos los datos a actualizar desde raíz
    json_empleado = {
        "nombre": payload.get("nombre"),
        "rol": payload.get("rol"),
    }
    json_empleado = {k: v for k, v in json_empleado.items() if v is not None}

    # 4. Completamos el payload con el estado actual para conservar campos no enviados
    current_payload = (
        db_empleado.data_json if isinstance(db_empleado.data_json, dict) else {}
    )
    current_root = {
        "cedula": db_empleado.cedula,
        "nombre": db_empleado.nombre,
        "rol": db_empleado.rol,
    }
    payload = {**current_root, **payload}
    payload.update(json_empleado)

    if (
        payload.get("jsonDirector") is None
        and current_payload.get("jsonDirector") is not None
    ):
        payload["jsonDirector"] = current_payload.get("jsonDirector")

    # 5. Actualizamos solo los campos que vengan (parcial)
    empleado_actualizado = crud_empleado.update_empleado(
        db, empleado_cedula, EmpleadoUpdate(**json_empleado), data_json=payload
    )

    # 6. Devolvemos solo el contenido guardado en data_json
    return _responder_data_json(empleado_actualizado, payload)


# Funcion para poder reemplazar a un empleado usando Put (modificada)
@router.put("/{empleado_cedula}", status_code=200)
def reemplazar_empleado(
    empleado_cedula: int, mensaje: EmpleadoMessagePut, db: Session = Depends(get_db)
):
    # 1. Obtenemos el payload completo
    payload = mensaje.model_dump(by_alias=True, exclude_none=False)

    # 2. Verificamos si existe el empleado
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede reemplazar: Empleado no encontrado."
        )

    # 3. Extraemos los datos completos desde raíz
    json_empleado = {
        "nombre": payload.get("nombre"),
        "rol": payload.get("rol"),
    }

    if not json_empleado["nombre"] or not json_empleado["rol"]:
        raise HTTPException(
            status_code=400,
            detail="Faltan datos obligatorios: nombre y rol para reemplazar.",
        )

    # 4. Reemplazamos todos los campos del empleado
    empleado_reemplazado = crud_empleado.put_empleado(
        db, empleado_cedula, EmpleadoPut(**json_empleado), data_json=payload
    )

    # 5. Devolvemos solo el contenido guardado en data_json
    return _responder_data_json(empleado_reemplazado, payload)


# Funcion para poder eliminar a un empleado
@router.delete("/{empleado_cedula}", status_code=204)
def eliminar_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    # Verificamos existencia
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede eliminar: Empleado no encontrado."
        )

    # Verificamos si tiene registros de labor asociados
    tiene_registros = (
        db.query(RegistroLabor)
        .filter(RegistroLabor.empleado_cedula == empleado_cedula)
        .first()
    )
    if tiene_registros:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el empleado tiene registros de labor asociados.",
        )

    crud_empleado.delete_empleado(db, empleado_cedula)
    return Response(status_code=204)
