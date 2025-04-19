from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the search router
from backend.src.endpoints import search

app = FastAPI(title="LLM Mobile Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the search router
app.include_router(search.router, prefix="/api") # Add a prefix like /api

@app.get("/")
async def root():
    return {"message": "Welcome to LLM Mobile Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 