# APIDevOps

API REST para la gestión de empleados, labores y registro de labores, construida con **FastAPI**, **SQLAlchemy** y **PostgreSQL**. Incluye soporte para Docker, pruebas automatizadas y despliegue en Railway.

## 🆕 Novedades en V2

✅ **Monitoreo y Observabilidad Integrados**

- Métricas Prometheus (`/metrics`)
- Health checks (`/health`)
- Dashboards con Grafana
- Docker Compose con stack de observabilidad

✅ **Despliegue en AWS**

- Elastic Beanstalk + RDS PostgreSQL
- Script de despliegue automático
- Variables de entorno gestionadas
- SSL/TLS en BD

---

## Tabla de Contenidos

- [Tecnologías](#tecnologías)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Requisitos Previos](#requisitos-previos)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
- [Pruebas](#pruebas)
- [Despliegue](#despliegue)

---

## Tecnologías

| Componente    | Tecnología              |
| ------------- | ----------------------- |
| Framework     | FastAPI                 |
| ORM           | SQLAlchemy              |
| Validación    | Pydantic                |
| Base de datos | PostgreSQL 17           |
| Servidor ASGI | Uvicorn                 |
| Contenedores  | Docker / Docker Compose |
| Testing       | Pytest + HTTPX (SQLite) |
| Despliegue    | AWS EB + RDS            |
| Monitoreo     | Prometheus + Grafana    |
| Logs          | Logging local estándar  |

---

## Arquitectura del Proyecto

```
app/
├── main.py                  # Punto de entrada de la aplicación
├── api/
│   └── v1/
│       ├── api.py           # Router principal v1
│       └── endpoints/
│           ├── empleados.py        # CRUD Empleados
│           ├── labores.py          # CRUD Labores
│           └── registro_labores.py # CRUD Registro de Labores
├── core/
│   ├── config.py            # Configuración con variables de entorno
│   ├── dependencies.py      # Inyección de dependencias (sesión DB)
│   └── security.py          # (Reservado para autenticación)
├── crud/
│   ├── crud_empleado.py     # Operaciones CRUD Empleado
│   ├── crud_labor.py        # Operaciones CRUD Labor
│   └── crud_registro_labor.py # Operaciones CRUD Registro Labor
├── db/
│   ├── base.py              # Importación de modelos para metadata
│   └── session.py           # Engine y SessionLocal de SQLAlchemy
├── models/
│   ├── empleado.py          # Modelo ORM Empleado
│   ├── labor.py             # Modelo ORM Labor
│   └── registro_labor.py   # Modelo ORM RegistroLabor
└── schemas/
    ├── empleado.py          # Schemas Pydantic Empleado
    ├── labor.py             # Schemas Pydantic Labor
    └── registro_labor.py   # Schemas Pydantic RegistroLabor
tests/
├── conftest.py              # Fixtures de pruebas (SQLite en memoria)
├── test_empleados.py
├── test_labores.py
└── test_registro_labores.py
```

---

## Modelos de Datos

### Empleado

| Campo    | Tipo    | Descripción         |
| -------- | ------- | ------------------- |
| `cedula` | Integer | Cédula (PK)         |
| `nombre` | String  | Nombre del empleado |
| `rol`    | String  | Rol o cargo         |

### Labor

| Campo           | Tipo   | Descripción                   |
| --------------- | ------ | ----------------------------- |
| `codigo_labor`  | String | Código único de la labor (PK) |
| `nombre`        | String | Nombre de la labor            |
| `unidad_medida` | String | Unidad de medida              |
| `precio`        | Float  | Precio por unidad             |
| `observacion`   | String | Observación (opcional)        |

### RegistroLabor

| Campo             | Tipo    | Descripción                 |
| ----------------- | ------- | --------------------------- |
| `id`              | Integer | ID autoincremental (PK)     |
| `empleado_cedula` | Integer | FK → `empleados.cedula`     |
| `codigo_labor`    | String  | FK → `labores.codigo_labor` |
| `fecha`           | Date    | Fecha del registro          |
| `cantidad`        | Float   | Cantidad realizada          |
| `observacion`     | String  | Observación (opcional)      |

---

## Endpoints de la API

Base URL: `/api/v1`

### Empleados (`/api/v1/empleados`)

| Método   | Ruta                 | Descripción                    | Status |
| -------- | -------------------- | ------------------------------ | ------ |
| `POST`   | `/`                  | Crear empleado                 | 201    |
| `GET`    | `/`                  | Listar todos los empleados     | 200    |
| `GET`    | `/{empleado_cedula}` | Obtener empleado por cédula    | 200    |
| `PATCH`  | `/{empleado_cedula}` | Actualizar campos parcialmente | 200    |
| `PUT`    | `/{empleado_cedula}` | Reemplazar empleado completo   | 200    |
| `DELETE` | `/{empleado_cedula}` | Eliminar empleado              | 204    |

### Labores (`/api/v1/labores`)

| Método   | Ruta              | Descripción                    | Status |
| -------- | ----------------- | ------------------------------ | ------ |
| `POST`   | `/`               | Crear labor                    | 201    |
| `GET`    | `/`               | Listar todas las labores       | 200    |
| `GET`    | `/{codigo_labor}` | Obtener labor por código       | 200    |
| `PATCH`  | `/{codigo_labor}` | Actualizar campos parcialmente | 200    |
| `PUT`    | `/{codigo_labor}` | Reemplazar labor completa      | 200    |
| `DELETE` | `/{codigo_labor}` | Eliminar labor                 | 204    |

### Registro de Labores (`/api/v1/registrolabores`)

| Método   | Ruta                          | Descripción                      | Status |
| -------- | ----------------------------- | -------------------------------- | ------ |
| `POST`   | `/`                           | Crear registro de labor          | 201    |
| `GET`    | `/`                           | Listar todos los registros       | 200    |
| `GET`    | `/empleado/{empleado_cedula}` | Obtener registros por empleado   | 200    |
| `PATCH`  | `/{registro_id}`              | Actualizar registro parcialmente | 200    |
| `PUT`    | `/{registro_id}`              | Reemplazar registro completo     | 200    |
| `DELETE` | `/{registro_id}`              | Eliminar registro                | 204    |

> La documentación interactiva (Swagger UI) está disponible en la ruta raíz `/` o directamente en `/docs`.

---

## Requisitos Previos

- **Python** 3.12+
- **Docker** y **Docker Compose** (para la base de datos)
- Variables de entorno configuradas (ver sección siguiente)

---

## Configuración

La aplicación carga sus variables de entorno desde un archivo `.env.{ENV}` según el valor de la variable de entorno `ENV`. Crea los archivos necesarios:

### `.env.development`

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=apidevops_dev
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@localhost:5432/apidevops_dev
```

### `.env.production`

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=apidevops_prod
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@host_produccion:5432/apidevops_prod
```

> Para Docker Compose, asegúrate de tener un archivo `.env` en la raíz con `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB_DEV`.

---

## Ejecución

### Desarrollo local (con Docker para la DB)

```bash
# Levantar PostgreSQL en Docker y ejecutar la app en modo desarrollo
./run_dev.sh
```

Esto ejecuta:

1. `docker compose up db_dev -d` — Inicia el contenedor de PostgreSQL.
2. `fastapi dev app/main.py` — Inicia la API con recarga automática.

### Solo Docker (app + DB)

```bash
docker compose up --build
```

La API estará disponible en `http://localhost:8000`.

### Producción local

```bash
./run_prod.sh
```

### Instalar dependencias manualmente

```bash
pip install -r requirements.txt
```

---

## Monitoreo y Observabilidad (V2)

La versión 2 incluye observabilidad integrada con **Prometheus** (métricas) y **Grafana** (visualización).

### Endpoints de Monitoreo

- **`GET /health`**: Health check de la aplicación y estado de BD.
- **`GET /metrics`**: Métricas Prometheus en formato estándar.

Ejemplo:

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0", "database": "connected"}

curl http://localhost:8000/metrics
# TYPE apidevops_requests_total counter
# apidevops_requests_total{endpoint="/api/v1/empleados",method="GET",status="200"} 5.0
```

### Métricas Expuestas

| Métrica                              | Tipo      | Descripción                                     |
| ------------------------------------ | --------- | ----------------------------------------------- |
| `apidevops_requests_total`           | Counter   | Total de requests por endpoint, método y status |
| `apidevops_request_duration_seconds` | Histogram | Duración de requests (p50, p95, p99)            |
| `apidevops_requests_errors_total`    | Counter   | Total de errores (4xx, 5xx)                     |
| `apidevops_db_connections_active`    | Gauge     | Conexiones activas a BD                         |

### Integración con Dashboards

#### Prometheus + Grafana (Self-hosted)

1. Prometheus scrape en `http://localhost:8000/metrics`.
2. Grafana importa datasource Prometheus.
3. Crea dashboard con métricas de APIDevOps.

#### Opcional: AlertManager

1. Agrega reglas de alerta en Prometheus.
2. Conecta AlertManager si quieres notificaciones.

### Despliegue en AWS EC2

Si quieres publicar el stack de monitoreo en AWS, usa el script:

```powershell
./scripts/deploy_monitoring_ec2.ps1 \
    -Ec2Host TU_IP_O_DNS \
    -SshKeyPath C:\ruta\a\tu\llave.pem \
    -ApiTarget apidevops-prod.eba-hiqy8jtp.us-east-2.elasticbeanstalk.com:80 \
    -GrafanaAdminPassword admin123
```

Requisitos:

1. Una EC2 con Docker y Docker Compose instalados.
2. Puertos abiertos en el Security Group: `3000` y `9090`.
3. Acceso SSH con tu llave `.pem`.

El script sube:

1. `docker-compose.monitoring.aws.yml`
2. `prometheus.yml` con el target apuntando a tu API de Elastic Beanstalk
3. La carpeta `grafana/` con datasource y dashboard provisionados

Luego levanta Grafana y Prometheus con `docker compose`.

---

## Pruebas

Las pruebas utilizan **SQLite** en memoria en lugar de PostgreSQL, configurado automáticamente en `tests/conftest.py`.

```bash
# Ejecutar todas las pruebas
pytest

# Con reporte de cobertura
pytest --cov=app
```

También puedes usar el script:

```bash
./run_test.sh
```

---

## Despliegue

### Railway

El proyecto incluye configuración para Railway:

- **Procfile**: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Dockerfile**: Imagen basada en `python:3.12-slim`.

Configura las variables de entorno (`DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `ENV`) en el dashboard de Railway.

### AWS (RDS + Elastic Beanstalk, automatizado)

Se incluye el script `scripts/deploy_aws_eb.ps1` para automatizar:

1. Validar credenciales AWS.
2. Crear RDS PostgreSQL (si no existe).
3. Crear aplicación y entorno de Elastic Beanstalk (si no existen).
4. Configurar variables de entorno (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`).
5. Desplegar la app.

Requisitos previos:

- AWS CLI instalado.
- EB CLI (`awsebcli`) instalado.
- Ejecutar desde la raíz del proyecto.

Ejecución:

```powershell
./scripts/deploy_aws_eb.ps1
```

El script solo solicita secretos en consola:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `POSTGRES_PASSWORD` (RDS)

Si quieres cambiar nombre de app, entorno, región o parámetros de RDS, puedes pasar argumentos:

```powershell
./scripts/deploy_aws_eb.ps1 -Region us-east-1 -AppName APIDevOps -EnvironmentName apidevops-prod
```

Al finalizar, imprime la URL pública y `/docs`.

---

## Manejo de Errores

La API incluye manejo global de excepciones:

- **Errores de SQLAlchemy** → Respuesta `500` con mensaje genérico de base de datos.
- **Excepciones no controladas** → Respuesta `500` con mensaje genérico del servidor.
- **Validaciones de negocio** → Respuestas `404` (no encontrado) y `409` (conflicto de duplicados o dependencias).

---

## Licencia

Este proyecto no especifica licencia actualmente.
