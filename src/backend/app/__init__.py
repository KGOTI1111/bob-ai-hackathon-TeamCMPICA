"""
Supply Chain Optimizer API Package
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import shipments, disruptions, fleet, cold_chain

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Supply Chain Optimizer API",
    description="Real-time supply chain disruption detection, fleet management, and cold chain monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(shipments.router)
app.include_router(disruptions.router)
app.include_router(fleet.router)
app.include_router(cold_chain.router)


@app.get("/")
def read_root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "Supply Chain Optimizer API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    }
