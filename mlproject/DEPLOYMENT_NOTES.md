
# Deployment Considerations

- Container image name: `iris-api`
- Listen on port `8000` (default in Dockerfile / uvicorn)
- Mount or bake `model.pkl` into the image. For reproducibility, train the model **inside** the same image version:
  ```bash
  docker run --rm -v "$PWD":/app iris-api python train_model.py
  ```
- Example run:
  ```bash
  docker run --rm -p 8000:8000 -v "$PWD/model.pkl":/app/model.pkl iris-api
  ```

## Cloud targets
- **Google Cloud Run**: set container port to 8000; configure CPU throttling, min instances 0, and memory 512–1024MiB.
- **AWS Elastic Beanstalk** (single container): upload image or Dockerrun JSON; configure health check path `/healthz`.
- **Kubernetes**: create a Deployment (1–2 replicas) + Service (LoadBalancer/Ingress). Configure liveness `/healthz` and readiness `/healthz` probes.

## Observability
- Logs go to stdout/stderr; aggregate via platform (Cloud Logging, CloudWatch, etc.).
- Consider adding request logging middleware if needed.

## Security
- Add CORS restrictions for known origins if exposing publicly.
- Prefer read-only mounts for `model.pkl`.



## Verification steps (post-deployment)

After the service is running (locally, in Docker, or in the cloud), you can verify it with:

- **Smoke test** (requires server reachable at :8000):
  ```bash
  python scripts/smoke_test.py
  ```

- **Unit tests** (run inside the container or local dev environment):
  ```bash
  pytest -q
  ```
  These validate input handling and health checks without needing the server.
