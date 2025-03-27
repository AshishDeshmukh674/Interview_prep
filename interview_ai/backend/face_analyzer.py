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
        
    def analyze_face(self, video_data: bytes) -> Dict[str, Any]:
        """
        Analyze face and eye contact from video data.
        """
        try:
            # Convert video data to frames
            frames = self._extract_frames_from_video(video_data)
            
            if not frames:
                logger.warning("No valid frames extracted from video")
                return {
                    "face_detection_rate": 0.0,
                    "eye_contact_rate": 0.0,
                    "confidence_score": 0.0,
                    "frame_count": 0,
                    "error": "No valid frames could be extracted from the video"
                }
            
            # Analyze each frame
            face_detection_rates = []
            eye_contact_rates = []
            confidence_scores = []
            
            for frame in frames:
                # Convert frame to RGB for MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(frame_rgb)
                
                if results.multi_face_landmarks:
                    # Face detected
                    face_detection_rates.append(1.0)
                    
                    # Get face landmarks
                    landmarks = results.multi_face_landmarks[0]
                    
                    # Calculate eye contact and confidence
                    eye_contact_rate = self._calculate_eye_contact(landmarks)
                    confidence_score = self._calculate_confidence(landmarks)
                    
                    eye_contact_rates.append(eye_contact_rate)
                    confidence_scores.append(confidence_score)
                else:
                    # No face detected
                    face_detection_rates.append(0.0)
                    eye_contact_rates.append(0.0)
                    confidence_scores.append(0.0)
            
            # Calculate averages (prevent division by zero)
            total_frames = len(frames)
            if total_frames == 0:
                return {
                    "face_detection_rate": 0.0,
                    "eye_contact_rate": 0.0,
                    "confidence_score": 0.0,
                    "frame_count": 0,
                    "error": "No frames to analyze"
                }
            
            # Calculate face detection rate
            avg_face_detection = sum(face_detection_rates) / total_frames if face_detection_rates else 0.0
            
            # Calculate eye contact rate only for frames where face was detected
            detected_frames = sum(1 for rate in face_detection_rates if rate > 0)
            avg_eye_contact = (sum(eye_contact_rates) / detected_frames) if detected_frames > 0 else 0.0
            
            # Calculate confidence score only for frames where face was detected
            avg_confidence = (sum(confidence_scores) / detected_frames) if detected_frames > 0 else 0.0
            
            return {
                "face_detection_rate": avg_face_detection,
                "eye_contact_rate": avg_eye_contact,
                "confidence_score": avg_confidence,
                "frame_count": total_frames,
                "detected_frames": detected_frames
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face: {str(e)}")
            return {
                "face_detection_rate": 0.0,
                "eye_contact_rate": 0.0,
                "confidence_score": 0.0,
                "frame_count": 0,
                "error": str(e)
            }
            
    def _extract_frames_from_video(self, video_data: bytes, max_frames: int = 30) -> List[np.ndarray]:
        """
        Extract frames from video data.
        """
        try:
            # Create a temporary file to store the video data
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name

            logger.info(f"Attempting to open video file: {temp_path}")
            
            # Open the video file
            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                logger.error("Error opening video file")
                return []

            frames = []
            frame_count = 0
            
            # Read frames until we have enough or reach the end
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frames.append(frame)
                frame_count += 1

            cap.release()
            
            logger.info(f"Successfully extracted {len(frames)} frames from video")
            
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Error deleting temporary file: {str(e)}")

            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
            
    def _calculate_eye_contact(self, landmarks) -> float:
        """
        Calculate eye contact rate based on face landmarks.
        """
        try:
            # Get eye landmarks
            left_eye = np.array([
                [landmarks.landmark[33].x, landmarks.landmark[33].y],
                [landmarks.landmark[246].x, landmarks.landmark[246].y],
                [landmarks.landmark[161].x, landmarks.landmark[161].y],
                [landmarks.landmark[160].x, landmarks.landmark[160].y],
                [landmarks.landmark[159].x, landmarks.landmark[159].y],
                [landmarks.landmark[158].x, landmarks.landmark[158].y]
            ], dtype=np.float32)
            
            right_eye = np.array([
                [landmarks.landmark[362].x, landmarks.landmark[362].y],
                [landmarks.landmark[398].x, landmarks.landmark[398].y],
                [landmarks.landmark[384].x, landmarks.landmark[384].y],
                [landmarks.landmark[385].x, landmarks.landmark[385].y],
                [landmarks.landmark[386].x, landmarks.landmark[386].y],
                [landmarks.landmark[387].x, landmarks.landmark[387].y]
            ], dtype=np.float32)
            
            # Calculate eye openness
            left_eye_openness = self._calculate_eye_openness(left_eye)
            right_eye_openness = self._calculate_eye_openness(right_eye)
            
            # Average eye openness
            avg_eye_openness = (left_eye_openness + right_eye_openness) / 2
            
            # Consider eye contact if eyes are open enough
            return float(avg_eye_openness > 0.3)
            
        except Exception as e:
            logger.error(f"Error calculating eye contact: {str(e)}")
            return 0.0
            
    def _calculate_eye_openness(self, eye_landmarks: np.ndarray) -> float:
        """
        Calculate eye openness ratio based on eye landmarks.
        """
        try:
            # Calculate vertical distance (height)
            height = np.linalg.norm(eye_landmarks[1] - eye_landmarks[4])
            
            # Calculate horizontal distance (width)
            width = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
            
            # Calculate aspect ratio
            aspect_ratio = height / width
            
            # Normalize aspect ratio to get openness ratio
            openness_ratio = min(1.0, aspect_ratio * 3)
            
            return float(openness_ratio)
            
        except Exception as e:
            logger.error(f"Error calculating eye openness: {str(e)}")
            return 0.0
            
    def _calculate_confidence(self, landmarks) -> float:
        """
        Calculate confidence score based on face landmarks.
        """
        try:
            # Get mouth landmarks
            mouth = np.array([
                [landmarks.landmark[61].x, landmarks.landmark[61].y],
                [landmarks.landmark[291].x, landmarks.landmark[291].y],
                [landmarks.landmark[199].x, landmarks.landmark[199].y],
                [landmarks.landmark[175].x, landmarks.landmark[175].y]
            ], dtype=np.float32)
            
            # Calculate mouth openness
            mouth_height = np.linalg.norm(mouth[1] - mouth[2])
            mouth_width = np.linalg.norm(mouth[0] - mouth[3])
            mouth_aspect_ratio = mouth_height / mouth_width
            
            # Get head pose (simplified)
            nose = np.array([landmarks.landmark[1].x, landmarks.landmark[1].y], dtype=np.float32)
            left_ear = np.array([landmarks.landmark[234].x, landmarks.landmark[234].y], dtype=np.float32)
            right_ear = np.array([landmarks.landmark[454].x, landmarks.landmark[454].y], dtype=np.float32)
            
            # Calculate head pose score
            ear_center = (left_ear + right_ear) / 2
            head_pose_score = 1.0 - min(1.0, np.linalg.norm(nose - ear_center) * 2)
            
            # Combine scores
            confidence_score = (mouth_aspect_ratio * 0.4 + head_pose_score * 0.6)
            
            return float(min(1.0, confidence_score))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0

# Create global instance
face_analyzer = FaceAnalyzer()

def analyze_face(video_data: bytes) -> Dict[str, Any]:
    """
    Analyze face and eye contact from video data.
    """
    return face_analyzer.analyze_face(video_data) 