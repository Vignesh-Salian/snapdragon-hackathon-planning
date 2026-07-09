"""
face_client.py
HemaGrid AI - Face Verification Service Client

Sends donor images to the Face Recognition module to check for duplicate enrollments.
"""

import httpx

FACE_RECOGNITION_URL = "http://127.0.0.1:8000/api/v1/donor/verify"

async def check_donor_duplicate(image_bytes: bytes) -> dict:
    """
    Uploads raw image bytes to the Face Verification service to identify duplicates.
    """
    files = {
        "image": ("check.jpg", image_bytes, "image/jpeg")
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Send image as multipart form upload
            response = await client.post(FACE_RECOGNITION_URL, files=files)
            
            # The face recognition API returns 409 Conflict when a duplicate is found,
            # which we parse here.
            if response.status_code in [200, 409]:
                return response.json()
            else:
                return {"status": "error", "message": f"Face Recognition returned code: {response.status_code}"}
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Connection to Face Verification failed: {str(e)}"}
