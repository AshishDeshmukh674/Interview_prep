import logging
from typing import Dict, Any
import numpy as np
import librosa
import io
from pydub import AudioSegment

logger = logging.getLogger(__name__)

def analyze_voice(video_data: bytes) -> Dict[str, Any]:
    """
    Analyze voice characteristics from video data.
    """
    try:
        # Convert video data to audio
        audio_data = _extract_audio_from_video(video_data)
        
        # Analyze various voice characteristics
        speech_rate = _analyze_speech_rate(audio_data)
        pitch_analysis = _analyze_pitch(audio_data)
        volume_analysis = _analyze_volume(audio_data)
        
        # Calculate overall voice quality score
        voice_score = _calculate_voice_score(
            speech_rate,
            pitch_analysis,
            volume_analysis
        )
        
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

def _extract_audio_from_video(video_data: bytes) -> np.ndarray:
    """
    Extract audio data from video bytes.
    """
    try:
        # Create a BytesIO object from the video data
        video_stream = io.BytesIO(video_data)
        
        # Convert video to audio using pydub
        video = AudioSegment.from_file(video_stream)
        audio = video.set_channels(1).set_frame_rate(44100)
        
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        return samples
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise

def _analyze_speech_rate(audio_data: np.ndarray) -> float:
    """
    Analyze speech rate (words per minute).
    """
    try:
        # Get onset frames
        onset_frames = librosa.onset.onset_detect(y=audio_data, sr=44100)
        
        # Calculate speech rate (words per minute)
        duration = librosa.get_duration(y=audio_data, sr=44100)
        if duration > 0:
            return len(onset_frames) / duration * 60
        return 0
        
    except Exception as e:
        logger.error(f"Error analyzing speech rate: {str(e)}")
        return 0

def _analyze_pitch(audio_data: np.ndarray) -> Dict[str, float]:
    """
    Analyze pitch characteristics.
    """
    try:
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=44100)
        
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

def _analyze_volume(audio_data: np.ndarray) -> Dict[str, float]:
    """
    Analyze volume characteristics.
    """
    try:
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio_data)
        mean_volume = float(np.mean(rms))
        volume_variation = float(np.std(rms))
        
        return {
            "mean_volume": mean_volume,
            "volume_variation": volume_variation
        }
        
    except Exception as e:
        logger.error(f"Error analyzing volume: {str(e)}")
        return {"mean_volume": 0, "volume_variation": 0}

def _calculate_voice_score(speech_rate: float, 
                          pitch_analysis: Dict[str, float], 
                          volume_analysis: Dict[str, float]) -> float:
    """
    Calculate overall voice quality score.
    """
    try:
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
        
    except Exception as e:
        logger.error(f"Error calculating voice score: {str(e)}")
        return 0.0 