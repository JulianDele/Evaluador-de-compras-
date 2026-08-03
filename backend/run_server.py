#!/usr/bin/env python3
"""
Run FastAPI server with built-in CORS middleware.
Execute with: python run_server.py
"""
import uvicorn

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗", flush=True)
    print("║  Starting FastAPI server with CORS middleware             ║", flush=True)
    print("╚════════════════════════════════════════════════════════════╝", flush=True)
    
    # Import after print to show startup banner first
    from app.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

