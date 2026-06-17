import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.pdf import router as pdf_router
from routes.ai import router as ai_router

app = FastAPI(title="Resume Editor API")

app.router.routes.extend(pdf_router.routes)
app.router.routes.extend(ai_router.routes)

dist = os.path.join(os.path.dirname(__file__), "..", "client", "dist")
if os.path.isdir(dist):
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "resume-editor-fastapi"}


@app.get("/api/debug/routes")
async def debug_routes():
    return {
        "service": "resume-editor-fastapi",
        "routes": sorted(
            f"{','.join(sorted(route.methods))} {route.path}"
            for route in app.routes
            if hasattr(route, "methods")
        ),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
