# Guía de Monitoreo y Observabilidad - APIDevOps V2

## Descripción General

La API ahora incluye observabilidad integrada mediante:

- **Prometheus**: Recolección de métricas (requests, latencia, errores)
- **Grafana**: Visualización de métricas y dashboards
- **Health Checks**: Validación del estado de la aplicación

---

## 1. Métricas Prometheus

### Acceso a métricas

```bash
curl http://localhost:8000/metrics
```

Formato estándar Prometheus, compatible con Grafana, Datadog, New Relic, etc.

### Métricas disponibles

#### `apidevops_requests_total` (Counter)

Total de requests procesados, etiquetados por:

- `method`: GET, POST, PUT, PATCH, DELETE
- `endpoint`: ruta (/api/v1/empleados, /api/v2/labores, etc.)
- `status`: código HTTP (200, 201, 400, 500, etc.)

**Ejemplo:**

```
apidevops_requests_total{endpoint="/api/v1/empleados",method="GET",status="200"} 42.0
apidevops_requests_total{endpoint="/api/v1/empleados",method="POST",status="201"} 10.0
apidevops_requests_total{endpoint="/api/v1/empleados",method="GET",status="404"} 2.0
```

#### `apidevops_request_duration_seconds` (Histogram)

Duración de requests, genera automáticamente percentiles:

- `_bucket` (p50, p95, p99, p999)
- `_sum` (suma total)
- `_count` (cantidad de muestras)

**Ejemplo:**

```
apidevops_request_duration_seconds_bucket{endpoint="/api/v1/empleados",method="GET",le="0.005"} 30.0
apidevops_request_duration_seconds_bucket{endpoint="/api/v1/empleados",method="GET",le="0.01"} 38.0
apidevops_request_duration_seconds_sum{endpoint="/api/v1/empleados",method="GET"} 0.450
apidevops_request_duration_seconds_count{endpoint="/api/v1/empleados",method="GET"} 42.0
```

#### `apidevops_requests_errors_total` (Counter)

Errores totales, etiquetados por:

- `method`: método HTTP
- `endpoint`: ruta
- `error_type`: "client_error" (4xx) o "server_error" (5xx)

**Ejemplo:**

```
apidevops_requests_errors_total{endpoint="/api/v1/empleados",error_type="client_error",method="POST"} 3.0
apidevops_requests_errors_total{endpoint="/api/v1/empleados",error_type="server_error",method="GET"} 1.0
```

#### `apidevops_db_connections_active` (Gauge)

Conexiones activas a PostgreSQL en tiempo real.

---

## 2. Health Checks

### Endpoint `/health`

```bash
curl http://localhost:8000/health

{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

Ideal para Kubernetes liveness/readiness probes o load balancers.

---

## 3. Integración con Herramientas (V2)

### 3.1 Grafana (Self-hosted)

**Setup:**

```bash
docker compose -f docker-compose.monitoring.yml up -d

# Ingresa a http://localhost:3000 (usuario: admin, pass: admin)
# El datasource y el dashboard se cargan automáticamente
```

**Dashboard incluido:**

- `APIDevOps Observability`
- `Request Rate (req/s)`
- `Error Rate (errors/s)`
- `P95 Latency (seconds)`
- `Top Endpoints (requests)`
- `Total Requests`
- `Total Errors`
- `Health Check`

**Queries útiles:**

```promql
# Request rate (req/s)
rate(apidevops_requests_total[1m])

# Latencia p95
histogram_quantile(0.95, apidevops_request_duration_seconds_bucket)

# Error rate
rate(apidevops_requests_errors_total[5m])

# Requests por endpoint
sum(apidevops_requests_total) by (endpoint)
```

### 3.2 Prometheus + AlertManager (Self-hosted)

**prometheus.yml:**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "apidevops"
    static_configs:
      - targets: ["app:8000"]
    metrics_path: "/metrics"
```

**Alertas:**

```yaml
# alert.rules.yml
- alert: HighErrorRate
  expr: rate(apidevops_requests_errors_total[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate detected"

- alert: SlowRequests
  expr: histogram_quantile(0.95, apidevops_request_duration_seconds_bucket) > 1
  for: 10m
  annotations:
    summary: "API latency too high"
```

---

## 4. Local Testing

### Docker Compose con monitoreo

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/apidevops

  db:
    image: postgres:17
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: password

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

```bash
docker compose -f docker-compose.monitoring.yml up

# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
# API: http://localhost:8000
# Métricas: http://localhost:8000/metrics
```

### Dashboard listo para demo

Si levantas `docker compose -f docker-compose.monitoring.yml up`, Grafana carga automáticamente:

1. La datasource de Prometheus.
2. El dashboard `APIDevOps Observability`.
3. Paneles con requests, errores, latencia y endpoints más usados.

---

## 5. Alertas Recomendadas

| Alerta            | Condición         | Acción               |
| ----------------- | ----------------- | -------------------- |
| Error Rate Alto   | > 5% en 5 min     | Verificar logs, DB   |
| Latencia Alta     | P95 > 1s          | Optimizar queries    |
| DB No disponible  | Health check fail | Reiniciar DB         |
| Memory High       | > 80%             | Aumentar recursos EB |
| Requests > Límite | > 100 req/s       | Auto-scaling         |

---

## 6. Troubleshooting

### Métricas no actualizan

```bash
# Verificar endpoint
curl http://localhost:8000/metrics | head -20

# Verificar middleware está activo
# Debe ver requests en logs

# Reiniciar app si es necesario
```

### Prometheus no scrape datos

```bash
# Verificar target en Prometheus UI
http://localhost:9090/targets

# Debe estar `UP` en verde
# Si está RED, verificar URL y conectividad
```

---

## 7. Referencias

- [Prometheus Docs](https://prometheus.io/docs)
- [Grafana Docs](https://grafana.com/docs)

---

**Archivo generado como parte de APIDevOps V2 - Monitoreo y Observabilidad**
