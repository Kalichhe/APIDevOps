## Canary Deployment

### Estrategia de redirección
Se usan dos contenedores Docker detrás de un Nginx como load balancer.
El tráfico se distribuye por pesos: stable recibe 75% y canary 25%.

### URLs para validar
| URL | Descripción |
|---|---|
| http://3.23.248.40/health | Healthcheck (75% stable / 25% canary) |
| http://3.23.248.40:5000/health | Solo stable |
| http://3.23.248.40:5001/health | Solo canary |
| http://3.23.248.40/docs | Swagger general |
| http://3.23.248.40:5000/docs | Swagger stable |
| http://3.23.248.40:5001/docs | Swagger canary |

### Monitoreo de la estrategia
```bash
# Ver distribución del tráfico en tiempo real
for i in {1..20}; do
  curl -s http://3.23.248.40//health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'], d['version'])"
done

# Ver logs de cada versión
docker compose -f /home/ubuntu/app/docker-compose.yml logs api-stable
docker compose -f /home/ubuntu/app/docker-compose.yml logs api-canary
```