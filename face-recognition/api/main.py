"""
main.py
HemaGrid AI - Donor Verification FastAPI Server

Exposes endpoints to enroll donors, verify biometric records, and detect
duplicate entries.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from models.detector import FaceDetector
from database.db import DonorDatabase

app = FastAPI(
    title="HemaGrid AI - Donor Verification Service",
    version="1.0.0",
    description="Biometric donor registration and fraud prevention service."
)

# Initialize subsystems
detector = FaceDetector()
db = DonorDatabase()

# Similarity threshold for duplicate detection
# Confidence levels above 0.87 (Euclidean distance < ~0.15) represent the same person
SIMILARITY_THRESHOLD = 0.87

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "donor-verification"}

@app.post("/api/v1/donor/enroll")
async def enroll_donor(
    name: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Enrolls a donor by extracting face landmarks and storing them in SQLite database.
    """
    if not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name field cannot be empty."
        )

    # Read image contents
    image_bytes = await image.read()
    
    # Extract landmarks
    landmarks = detector.extract_landmarks(image_bytes)
    if landmarks is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biometric Error: No face detected in uploaded image. Please retry."
        )

    # Save to database
    try:
        donor_id = db.enroll_donor(name, landmarks)
        return {
            "status": "success",
            "donor_id": donor_id,
            "message": "Donor successfully enrolled"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Write Failure: {str(e)}"
        )

@app.post("/api/v1/donor/verify")
async def verify_donor(
    image: UploadFile = File(...)
):
    """
    Compares uploaded image against database records to detect duplicate enrollments.
    """
    image_bytes = await image.read()
    
    # Extract landmarks from input image
    input_landmarks = detector.extract_landmarks(image_bytes)
    if input_landmarks is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biometric Error: No face detected in uploaded image."
        )

    # Query recent enrollments
    recent_donors = db.get_recent_donors(days_limit=56)
    
    highest_similarity = 0.0
    matched_donor = None

    # Perform linear search vector similarity matching
    for donor in recent_donors:
        similarity = detector.calculate_similarity(input_landmarks, donor["landmarks"])
        if similarity > highest_similarity:
            highest_similarity = similarity
            matched_donor = donor

    # Evaluate duplicates
    if highest_similarity >= SIMILARITY_THRESHOLD and matched_donor is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "duplicate_detected": True,
                "confidence": round(highest_similarity, 2),
                "matched_donor": {
                    "id": matched_donor["id"],
                    "name": matched_donor["name"],
                    "enrolled_at": matched_donor["enrolled_at"]
                },
                "message": "Fraud Alert: This donor has already registered within the lockout window."
            }
        )

    return {
        "duplicate_detected": False,
        "confidence": round(highest_similarity, 2),
        "message": "No matching donor record found. Registration is safe to proceed."
    }
