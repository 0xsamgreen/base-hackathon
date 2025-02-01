from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import users
from .db.session import engine
from .models.user import Base
from .db.health import wait_for_db

# Wait for database to be ready
wait_for_db()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hackathon API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Welcome to Hackathon API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
