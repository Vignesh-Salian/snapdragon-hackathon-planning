"""Face landmark extraction.

On the phone / Snapdragon target this runs MediaPipe Face Mesh (468 landmarks →
1404 floats), ideally as a LiteRT `.tflite` model quantized to INT8 for the
Hexagon NPU. Where MediaPipe isn't installed (dev laptops, CI) it falls back to
a deterministic byte-derived embedding so the enroll/verify/duplicate logic is
fully runnable and testable without the heavy CV stack.
"""
from __future__ import annotations

import hashlib

import numpy as np

LANDMARK_DIM = 1404  # 468 landmarks × (x, y, z)


class NoFaceError(ValueError):
    """Raised when no face can be found in the image."""


def _try_mediapipe(image_bytes: bytes) -> np.ndarray | None:
    try:
        import cv2  # noqa: F401
        import mediapipe as mp
    except ImportError:
        return None
    npbuf = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(npbuf, cv2.IMREAD_COLOR)
    if img is None:
        raise NoFaceError("Image could not be decoded")
    with mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as mesh:
        res = mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not res.multi_face_landmarks:
        raise NoFaceError("No face detected in image")
    lm = res.multi_face_landmarks[0].landmark
    vec = np.array([c for p in lm for c in (p.x, p.y, p.z)], dtype=np.float32)
    return _normalize(vec)


def _fallback_embedding(image_bytes: bytes) -> np.ndarray:
    # Deterministic: identical image bytes → identical vector → distance 0.
    if not image_bytes or len(image_bytes) < 64:
        raise NoFaceError("No face detected (image too small / empty)")
    buf = bytearray()
    seed = image_bytes
    while len(buf) < LANDMARK_DIM:
        seed = hashlib.sha256(seed).digest()
        buf.extend(seed)
    # bytes → floats in [-1, 1]: bounded and near-orthogonal for different inputs,
    # so identical images → distance 0, different images → ~sqrt(2).
    arr = np.frombuffer(bytes(buf[:LANDMARK_DIM]), dtype=np.uint8).astype(np.float32)
    return _normalize(arr / 127.5 - 1.0)


def _normalize(vec: np.ndarray) -> np.ndarray:
    return vec / (float(np.linalg.norm(vec)) + 1e-9)


def extract_landmarks(image_bytes: bytes) -> np.ndarray:
    """Return a 1404-float normalized landmark vector, or raise NoFaceError."""
    vec = _try_mediapipe(image_bytes)
    if vec is None:
        vec = _fallback_embedding(image_bytes)
    return vec


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two landmark vectors."""
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))
