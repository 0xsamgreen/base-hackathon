import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="debug"
    )
