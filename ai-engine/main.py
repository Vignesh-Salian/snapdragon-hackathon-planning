"""HemaGrid AI Engine — FastAPI prediction server (port 8001).

Run:  python main.py    (or)   uvicorn main:app --port 8001
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(title="HemaGrid AI Engine", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(router)


@app.get("/health")
def health():
    # Report which execution provider is live so judges can see NPU vs CPU.
    try:
        from inference.predict import get_predictor

        p = get_predictor()
        return {"status": "ok", "provider": p.provider, "npu_active": p.npu_active()}
    except FileNotFoundError:
        return {"status": "degraded", "detail": "model.onnx not built yet"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
