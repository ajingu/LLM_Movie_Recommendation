# LLM Mobile Backend

A FastAPI-based backend server for the LLM Mobile application.

## Setup

1. Create a conda environment and activate it:
```bash
conda create -n llm_mobile python=3.11
conda activate llm_mobile
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

To start the server, run:
```bash
uvicorn src.main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 