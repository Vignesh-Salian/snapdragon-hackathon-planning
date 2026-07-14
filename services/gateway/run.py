"""Entry point: `python run.py` → HemaGrid backend on :8002 (per spec)."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8002, reload=True)
