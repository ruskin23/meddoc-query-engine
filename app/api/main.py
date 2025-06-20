from fastapi import FastAPI
from app.api.routes import ingest, extract, index, retrieve

app = FastAPI()

app.include_router(ingest.router, prefix="/ingest")
app.include_router(extract.router, prefix="/extract")
app.include_router(index.router, prefix="/index")
app.include_router(retrieve.router, prefix="/retrieve")
