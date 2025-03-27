import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import scipy.signal
import speech_recognition as sr
import librosa
from typing import Dict, Any
import logging
import os
from pydub import AudioSegment

mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def extract_audio_from_video(self, video_path: str) -> str:
        try:
            audio_path = video_path.rsplit('.', 1)[0] + '.wav'
            video = AudioSegment.from_file(video_path)
            video.export(audio_path, format="wav")
            return audio_path
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise

    def analyze_speech_rate(self, audio_path: str) -> float:
        try:
            y, sr = librosa.load(audio_path)
            # Get onset frames
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            # Calculate speech rate (words per minute)
            duration = librosa.get_duration(y=y, sr=sr)
            if duration > 0:
                return len(onset_frames) / duration * 60
            return 0
        except Exception as e:
            logger.error(f"Error analyzing speech rate: {str(e)}")
            return 0

    def analyze_pitch(self, audio_path: str) -> Dict[str, float]:
        try:
            y, sr = librosa.load(audio_path)
            # Extract pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            # Get mean pitch
            mean_pitch = np.mean(pitches[magnitudes > magnitudes.mean()])
            # Get pitch variation
            pitch_std = np.std(pitches[magnitudes > magnitudes.mean()])
            return {
                "mean_pitch": float(mean_pitch),
                "pitch_variation": float(pitch_std)
            }
        except Exception as e:
            logger.error(f"Error analyzing pitch: {str(e)}")
            return {"mean_pitch": 0, "pitch_variation": 0}

    def analyze_volume(self, audio_path: str) -> Dict[str, float]:
        try:
            y, sr = librosa.load(audio_path)
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y)
            mean_volume = float(np.mean(rms))
            volume_variation = float(np.std(rms))
            return {
                "mean_volume": mean_volume,
                "volume_variation": volume_variation
            }
        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return {"mean_volume": 0, "volume_variation": 0}

    def analyze_voice(self, video_path: str) -> Dict[str, Any]:
        try:
            # Extract audio from video
            audio_path = self.extract_audio_from_video(video_path)
            
            # Perform various analyses
            speech_rate = self.analyze_speech_rate(audio_path)
            pitch_analysis = self.analyze_pitch(audio_path)
            volume_analysis = self.analyze_volume(audio_path)

            # Calculate overall voice quality score
            voice_score = self._calculate_voice_score(
                speech_rate,
                pitch_analysis,
                volume_analysis
            )

            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

            return {
                "speech_rate": round(speech_rate, 2),
                "pitch_analysis": {
                    "mean_pitch": round(pitch_analysis["mean_pitch"], 2),
                    "pitch_variation": round(pitch_analysis["pitch_variation"], 2)
                },
                "volume_analysis": {
                    "mean_volume": round(volume_analysis["mean_volume"], 2),
                    "volume_variation": round(volume_analysis["volume_variation"], 2)
                },
                "voice_quality_score": round(voice_score, 2)
            }

        except Exception as e:
            logger.error(f"Error in voice analysis: {str(e)}")
            raise

    def _calculate_voice_score(self, speech_rate: float, pitch_analysis: Dict[str, float], 
                             volume_analysis: Dict[str, float]) -> float:
        # Ideal speech rate range (words per minute)
        ideal_speech_rate = 150
        speech_rate_score = max(0, 100 - abs(speech_rate - ideal_speech_rate) / 2)

        # Pitch variation score (higher variation is better for engagement)
        pitch_variation_score = min(100, pitch_analysis["pitch_variation"] * 10)

        # Volume variation score (moderate variation is good)
        volume_variation_score = min(100, volume_analysis["volume_variation"] * 20)

        # Weighted average of scores
        return (
            speech_rate_score * 0.4 +
            pitch_variation_score * 0.3 +
            volume_variation_score * 0.3
        )

def analyze_video():
    cap = cv2.VideoCapture(0)
    analysis_result = {}

    for _ in range(50):  # Analyze 50 frames
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            analysis_result["eye_contact"] = "Good" if check_eye_contact(results) else "Poor"
            analysis_result["head_position"] = "Stable" if check_head_position(results) else "Unstable"

    cap.release()
    return analysis_result

def check_eye_contact(results):
    return True  # Placeholder logic for eye contact detection

def check_head_position(results):
    return True  # Placeholder logic for head movement tracking

def analyze_voice(video_path: str) -> Dict[str, Any]:
    analyzer = VoiceAnalyzer()
    return analyzer.analyze_voice(video_path)
