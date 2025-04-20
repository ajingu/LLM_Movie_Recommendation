from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the routers
from backend.src.endpoints import search
from backend.src.endpoints import chat_search # Import the new chat router

app = FastAPI(title="LLM Mobile Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
app.include_router(search.router, prefix="/api", tags=["Keyword Search"])
app.include_router(chat_search.router, prefix="/api", tags=["Chat Search"]) # Include the chat router

@app.get("/")
async def root():
    return {"message": "Welcome to LLM Mobile Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}