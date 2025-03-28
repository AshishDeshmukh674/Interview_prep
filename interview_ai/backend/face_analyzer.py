import logging
import cv2
import numpy as np
import io
import mediapipe as mp
from typing import Dict, Any, List, Tuple
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceAnalyzer:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    async def analyze(self, video_data: bytes) -> Dict[str, float]:
        """
        Analyze face metrics from video data.
        """
        try:
            # Convert video data to numpy array
            nparr = np.frombuffer(video_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("Failed to decode video frame")
                return self._get_default_metrics()
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.face_mesh.process(frame_rgb)
            
            if not results.multi_face_landmarks:
                logger.warning("No face detected in frame")
                return self._get_default_metrics()
            
            # Get face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Calculate metrics
            eye_contact_rate = self._calculate_eye_contact(face_landmarks)
            face_detection_rate = 1.0  # Face was detected
            head_position_score = self._calculate_head_position(face_landmarks)
            
            return {
                "eye_contact_rate": eye_contact_rate,
                "face_detection_rate": face_detection_rate,
                "head_position_score": head_position_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face: {str(e)}")
            return self._get_default_metrics()
    
    def _calculate_eye_contact(self, face_landmarks) -> float:
        """
        Calculate eye contact rate based on face landmarks.
        """
        try:
            # Get eye landmarks
            left_eye = face_landmarks.landmark[33:46]  # Left eye landmarks
            right_eye = face_landmarks.landmark[246:259]  # Right eye landmarks
            
            # Calculate eye openness
            left_eye_openness = self._calculate_eye_openness(left_eye)
            right_eye_openness = self._calculate_eye_openness(right_eye)
            
            # Average eye openness
            eye_openness = (left_eye_openness + right_eye_openness) / 2
            
            # Normalize to 0-1 range
            return min(max(eye_openness, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating eye contact: {str(e)}")
            return 0.5
    
    def _calculate_eye_openness(self, eye_landmarks) -> float:
        """
        Calculate eye openness based on eye landmarks.
        """
        try:
            # Get vertical distance between upper and lower eyelids
            upper_lid = eye_landmarks[1].y
            lower_lid = eye_landmarks[4].y
            
            # Calculate eye height
            eye_height = abs(upper_lid - lower_lid)
            
            # Get horizontal distance between eye corners
            left_corner = eye_landmarks[0].x
            right_corner = eye_landmarks[3].x
            
            # Calculate eye width
            eye_width = abs(right_corner - left_corner)
            
            # Calculate aspect ratio
            aspect_ratio = eye_height / eye_width if eye_width > 0 else 0
            
            # Normalize to 0-1 range (typical range is 0.2-0.4)
            return min(max((aspect_ratio - 0.2) / 0.2, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating eye openness: {str(e)}")
            return 0.5
    
    def _calculate_head_position(self, face_landmarks) -> float:
        """
        Calculate head position score based on face landmarks.
        """
        try:
            # Get nose tip and face center
            nose_tip = face_landmarks.landmark[4]
            face_center = face_landmarks.landmark[1]  # Using nose bridge as reference
            
            # Calculate deviation from center
            x_deviation = abs(nose_tip.x - 0.5)  # 0.5 is center
            y_deviation = abs(nose_tip.y - 0.5)
            
            # Calculate total deviation
            total_deviation = (x_deviation + y_deviation) / 2
            
            # Convert to score (1.0 is perfect, 0.0 is completely off-center)
            return 1.0 - total_deviation
            
        except Exception as e:
            logger.error(f"Error calculating head position: {str(e)}")
            return 0.5
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """
        Return default metrics when analysis fails.
        """
        return {
            "eye_contact_rate": 0.5,
            "face_detection_rate": 0.0,
            "head_position_score": 0.5
        }

# Create global instance
face_analyzer = FaceAnalyzer()

def analyze_face(video_data: bytes) -> Dict[str, float]:
    """
    Analyze face metrics from video data.
    """
    return face_analyzer.analyze(video_data) 