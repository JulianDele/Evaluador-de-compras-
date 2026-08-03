#!/usr/bin/env python3
"""
Pure Starlette ASGI app that wraps FastAPI with proper CORS handling.
This bypasses Uvicorn's internal routing entirely.
Execute with: python starlette_wrapper.py
"""
import asyncio
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send
import uvicorn

print("╔════════════════════════════════════════════════════════════╗", flush=True)
print("║  Initializing Starlette wrapper with CORS                 ║", flush=True)
print("╚════════════════════════════════════════════════════════════╝", flush=True)


class StarletteCORSPreflight:
    """Pure ASGI middleware for CORS preflight - no BaseHTTPMiddleware overhead."""
    
    def __init__(self, app: ASGIApp):
        self.app = app
        print("✅ StarletteCORSPreflight initialized", flush=True)
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        print(f"🔵 StarletteCORSPreflight: {scope['method']} {scope['path']}", flush=True)
        
        if scope["method"] == "OPTIONS":
            print(f"📋 OPTIONS handled by wrapper: {scope['path']}", flush=True)
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Override status and headers for OPTIONS
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [
                            (b"access-control-allow-origin", b"*"),
                            (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, PATCH, OPTIONS"),
                            (b"access-control-allow-headers", b"content-type, authorization"),
                            (b"access-control-allow-credentials", b"true"),
                            (b"access-control-max-age", b"86400"),
                            (b"content-type", b"text/plain"),
                            (b"content-length", b"0"),
                        ],
                    })
                elif message["type"] == "http.response.body":
                    # Send empty body for OPTIONS
                    await send({
                        "type": "http.response.body",
                        "body": b"",
                        "more_body": False,
                    })
            
            # Call wrapped app with send wrapper
            await self.app(scope, receive, send_wrapper)
        else:
            # For non-OPTIONS requests, pass through
            await self.app(scope, receive, send)


# Import FastAPI app
from app.main import app as fastapi_app

print(f"✅ FastAPI app imported: {type(fastapi_app)}", flush=True)

# Wrap with pure ASGI middleware
app = StarletteCORSPreflight(fastapi_app)

print("╔════════════════════════════════════════════════════════════╗", flush=True)
print("║  Starlette wrapper ready                                  ║", flush=True)
print("╚════════════════════════════════════════════════════════════╝", flush=True)

if __name__ == "__main__":
    print("Starting Uvicorn with Starlette wrapper...", flush=True)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
