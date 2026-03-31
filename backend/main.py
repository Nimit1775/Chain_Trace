from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import graph, analysis, ai

app = FastAPI(title="ChainTrace AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.router,    prefix="/api/graph",    tags=["Graph"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(ai.router,       prefix="/api/ai",       tags=["AI Agent"])

@app.get("/")
def root():
    return {"status": "ChainTrace AI is running"}
