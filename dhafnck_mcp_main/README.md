# quickstart

```bash
cd dhafnck_mcp_main
```

## Start the container (creates if doesn't exist)

```bash
docker system prune -f && docker-compose -f docker/docker-compose.redis.yml down && docker-compose -f docker/docker-compose.redis.yml build --no-cache dhafnck-mcp && ./scripts/manage-docker.sh start
```


## Stop the running container

```bash
./scripts/manage-docker.sh stop
```

## Restart the container

```bash
## Restart the container
./scripts/manage-docker.sh restart
```

## Show live logs (Ctrl+C to exit)

```bash
./scripts/manage-docker.sh logs
```

## Check container status and resource usage

```bash
./scripts/manage-docker.sh status
```

## Verify server health

```bash
./scripts/manage-docker.sh health
```

## Open shell inside container for debugging

```bash
./scripts/manage-docker.sh shell
```

## Remove container (preserves data volumes)

```bash
./scripts/manage-docker.sh remove
```

## Complete cleanup and rebuild

```bash
./scripts/manage-docker.sh cleanup
```

## Show help and available commands

```bash
./scripts/manage-docker.sh help
```
