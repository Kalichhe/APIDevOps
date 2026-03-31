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
    EmpleadoRead,
    EmpleadoUpdate,
)
from app.crud import crud_empleado
from app.models.registro_labor import RegistroLabor

router = APIRouter()


# Funcion para crear a un Empleado
@router.post("/", status_code=201)
def crear_empleado(mensaje: EmpleadoMessageCreate, db: Session = Depends(get_db)):

    # 1. Obtenemos el payload completo directamente del modelo
    # Nota: model.model_dump() mantiene la estructura tal como llegó
    payload = mensaje.model_dump(by_alias=True, exclude_none=False)

    # 2. Validamos la estructura esperada
    try:
        json_director = payload.get("jsonDirector", {})
        json_empleado = json_director.get("jsonEmpleado", {})

        cedula = json_empleado.get("cedula")
        nombre = json_empleado.get("nombre")
        rol = json_empleado.get("rol")

        if (
            cedula is None
            or nombre is None
            or rol is None
            or str(nombre).strip() == ""
            or str(rol).strip() == ""
        ):
            raise ValueError("Faltan campos en jsonDirector.jsonEmpleado")
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

    # 5. Devolvemos el JSON exactamente como llegó
    return payload


# Funcion para buscar empleados
@router.get("/", response_model=list[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db)):
    return crud_empleado.get_empleados(db)


# Funcion para buscar a un empleado
@router.get("/{empleado_cedula}", response_model=EmpleadoRead)
def obtener_empleado(empleado_cedula: int, db: Session = Depends(get_db)):
    empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not empleado:
        raise HTTPException(
            status_code=404,
            detail=f"Empleado con cédula {empleado_cedula} no encontrado.",
        )
    return empleado


# Funcion para poder modificar a un empleado usando Patch (modificada)
@router.patch("/{empleado_cedula}", status_code=200)
def actualizar_empleado(
    empleado_cedula: int, mensaje: EmpleadoMessageUpdate, db: Session = Depends(get_db)
):
    # 1. Obtenemos el payload completo
    payload = mensaje.model_dump(by_alias=True, exclude_none=False)

    # 2. Verificamos si existe el empleado
    db_empleado = crud_empleado.get_empleado(db, empleado_cedula)
    if not db_empleado:
        raise HTTPException(
            status_code=404, detail="No se puede actualizar: Empleado no encontrado."
        )

    # 3. Extraemos los datos a actualizar desde jsonDirector.jsonEmpleado
    json_director = payload.get("jsonDirector", {})
    json_empleado = json_director.get("jsonEmpleado", {})

    # 4. Actualizamos solo los campos que vengan (parcial)
    empleado_actualizado = crud_empleado.update_empleado(
        db, empleado_cedula, EmpleadoUpdate(**json_empleado), data_json=payload
    )

    # 5. Devolvemos el JSON exactamente como llegó
    return payload


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

    # 3. Extraemos los datos completos desde jsonDirector.jsonEmpleado
    json_director = payload.get("jsonDirector", {})
    json_empleado = json_director.get("jsonEmpleado", {})

    if not json_empleado.get("nombre") or not json_empleado.get("rol"):
        raise HTTPException(
            status_code=400,
            detail="Faltan datos obligatorios en jsonDirector.jsonEmpleado para reemplazar.",
        )

    # 4. Reemplazamos todos los campos del empleado
    empleado_reemplazado = crud_empleado.put_empleado(
        db, empleado_cedula, EmpleadoPut(**json_empleado), data_json=payload
    )

    # 5. Devolvemos el JSON exactamente como llegó
    return payload


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
