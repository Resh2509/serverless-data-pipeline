from fastapi import FastAPI

from analytics.metrics import (
    generate_metrics,
    posts_per_user,
    pipeline_health_summary,
    recent_pipeline_runs,
)

app = FastAPI(title="Serverless Data Pipeline API")

@app.get("/")
def root():
    return {"message": "Serverless Data Pipeline API is running"}

@app.get("/metrics")
def get_metrics():
    return generate_metrics()

@app.get("/posts-per-user")
def get_posts_per_user():
    df = posts_per_user()
    return df.to_dict(orient="records")

@app.get("/pipeline-health")
def get_pipeline_health():
    return pipeline_health_summary()

@app.get("/pipeline-runs")
def get_pipeline_runs(limit: int = 10):
    return recent_pipeline_runs(limit=limit)