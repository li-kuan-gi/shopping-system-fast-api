from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import cart

app = FastAPI(title="Shopping System API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "success", "message": "Shopping System API is running"}


