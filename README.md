# Green Power Hours

See when UK electricity is greener and cheaper, using live NESO carbon intensity and Octopus Agile prices.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs

## Layout

- `frontend/` Next.js 14
- `backend/` FastAPI, Postgres snapshots, Redis cache
- `backend/app/ml/` forecasting and recommendations
- `backend/app/jobs/` snapshot and retrain workers
