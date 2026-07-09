"""
detector.py
HemaGrid AI - Face Landmark Extractor

Handles face detection and landmark extraction using MediaPipe Face Mesh.
Decodes raw image bytes and generates standard 468-point landmark topologies
used as biometric signatures.
"""

import cv2
import numpy as np
import mediapipe as mp

class FaceDetector:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5
        )

    def extract_landmarks(self, image_bytes: bytes):
        """
        Decodes raw image bytes, runs face detection, and returns a flat list
        of 1404 floats (468 points * 3 coordinates x, y, z).
        
        Returns:
            list: Flat list of float coordinates, or None if no face is detected.
        """
        # Decode byte stream to OpenCV BGR image format
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        # MediaPipe requires RGB format
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_img)

        if not results.multi_face_landmarks:
            return None

        # Extract first detected face
        face_landmarks = results.multi_face_landmarks[0]
        
        flat_landmarks = []
        for landmark in face_landmarks.landmark:
            flat_landmarks.append(float(landmark.x))
            flat_landmarks.append(float(landmark.y))
            flat_landmarks.append(float(landmark.z))
            
        return flat_landmarks

    @staticmethod
    def calculate_similarity(landmarks_a, landmarks_b) -> float:
        """
        Calculates similarity using Euclidean distance over the landmark topologies.
        Returns a confidence score between 0.0 (no similarity) and 1.0 (exact match).
        """
        arr_a = np.array(landmarks_a)
        arr_b = np.array(landmarks_b)
        
        # Calculate Euclidean Distance
        distance = np.linalg.norm(arr_a - arr_b)
        
        # Normalize distance into a confidence score
        # Hand-tuned threshold: distance < 0.15 indicates identical person
        if distance == 0:
            return 1.0
            
        # Convert distance to confidence scale (near 0 distance -> near 1.0 confidence)
        confidence = 1.0 / (1.0 + distance)
        return float(confidence)
