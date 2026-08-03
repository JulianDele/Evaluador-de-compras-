"""
Wrapper ASGI que maneja CORS preflight OPTIONS antes de pasar a FastAPI.
Ejecutar con: uvicorn asgi_wrapper:app
"""
import sys

# Print de diagnóstico
print("╔════════════════════════════════════════════════════════════╗", flush=True)
print("║  ASGI WRAPPER LOADING...                                 ║", flush=True)
print("╚════════════════════════════════════════════════════════════╝", flush=True)

print(f"Python: {sys.executable}", flush=True)
print(f"Working dir: {sys.path[0]}", flush=True)

# Importar FastAPI app
try:
    from app.main import _fastapi_app
    print("✅ FastAPI app imported successfully", flush=True)
except Exception as e:
    print(f"❌ Error importing FastAPI app: {e}", flush=True)
    raise


class CORSASGIApp:
    """ASGI middleware que maneja CORS preflight OPTIONS."""
    
    def __init__(self, app):
        self.app = app
        print(f"✅ CORSASGIApp initialized with app: {type(app)}", flush=True)
    
    async def __call__(self, scope, receive, send):
        """Handle ASGI scope."""
        print(f"🔵 CORSASGIApp called - Type: {scope.get('type')}, Method: {scope.get('method', 'N/A')}, Path: {scope.get('path', 'N/A')}", flush=True)
        
        if scope["type"] == "http":
            if scope["method"] == "OPTIONS":
                print(f"📋 OPTIONS intercepted for: {scope.get('path')}", flush=True)
                # Respond with 200 OK and CORS headers
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"access-control-allow-origin", b"*"],
                        [b"access-control-allow-methods", b"GET, POST, PUT, DELETE, PATCH, OPTIONS"],
                        [b"access-control-allow-headers", b"content-type, authorization"],
                        [b"access-control-allow-credentials", b"true"],
                        [b"access-control-max-age", b"86400"],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"",
                })
                return
        
        # Pass to FastAPI
        print(f"➡️  Passing to FastAPI: {scope.get('method', 'N/A')} {scope.get('path', 'N/A')}", flush=True)
        await self.app(scope, receive, send)


# Create ASGI app
app = CORSASGIApp(_fastapi_app)
print("╔════════════════════════════════════════════════════════════╗", flush=True)
print("║  ASGI WRAPPER READY                                       ║", flush=True)
print("╚════════════════════════════════════════════════════════════╝", flush=True)

