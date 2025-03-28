import logging
from typing import Dict, Any
import numpy as np
import librosa
import io
from pydub import AudioSegment
import sounddevice as sd
import asyncio
import soundfile as sf

logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    def __init__(self):
        self.sample_rate = 16000
        self.hop_length = 512
        self.n_fft = 2048

    async def analyze(self, video_data: bytes) -> Dict[str, float]:
        """
        Analyze voice metrics from video data.
        """
        try:
            # Extract audio from video data
            audio_data = self._extract_audio(video_data)
            if audio_data is None:
                logger.error("Failed to extract audio from video")
                return self._get_default_metrics()
            
            # Load audio data using librosa
            y, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate)
            
            # Calculate metrics
            speech_rate = self._calculate_speech_rate(y)
            volume = self._calculate_volume(y)
            pitch = self._calculate_pitch(y)
            fluency = self._calculate_fluency(y)
            
            return {
                "speech_rate": speech_rate,
                "volume": volume,
                "pitch": pitch,
                "fluency": fluency
            }
            
        except Exception as e:
            logger.error(f"Error analyzing voice: {str(e)}")
            return self._get_default_metrics()
    
    def _extract_audio(self, video_data: bytes) -> bytes:
        """
        Extract audio data from video data.
        """
        try:
            # Create a temporary file to store the video data
            with io.BytesIO(video_data) as video_buffer:
                # Use soundfile to read the audio data
                audio_data, _ = sf.read(video_buffer)
                
                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # Convert to 16-bit PCM
                audio_data = (audio_data * 32767).astype(np.int16)
                
                # Save to bytes buffer
                with io.BytesIO() as audio_buffer:
                    sf.write(audio_buffer, audio_data, self.sample_rate, format='WAV')
                    return audio_buffer.getvalue()
                    
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None
    
    def _calculate_speech_rate(self, y: np.ndarray) -> float:
        """
        Calculate speech rate (words per minute).
        """
        try:
            # Get onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate)
            
            # Find onset frames
            onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env)
            
            # Convert frames to time
            onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
            
            # Calculate average time between onsets
            if len(onset_times) > 1:
                intervals = np.diff(onset_times)
                avg_interval = np.mean(intervals)
                
                # Convert to words per minute (assuming each onset is a word)
                words_per_minute = 60 / avg_interval
                
                # Normalize to 0-1 range (typical range is 100-200 WPM)
                return min(max((words_per_minute - 100) / 100, 0.0), 1.0)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating speech rate: {str(e)}")
            return 0.5
    
    def _calculate_volume(self, y: np.ndarray) -> float:
        """
        Calculate average volume level.
        """
        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y)[0]
            
            # Calculate average RMS
            avg_rms = np.mean(rms)
            
            # Normalize to 0-1 range
            return min(max(avg_rms * 10, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating volume: {str(e)}")
            return 0.5
    
    def _calculate_pitch(self, y: np.ndarray) -> float:
        """
        Calculate average pitch variation.
        """
        try:
            # Get pitch track
            pitches, magnitudes = librosa.piptrack(y=y, sr=self.sample_rate)
            
            # Get mean pitch for voiced frames
            voiced_frames = magnitudes > 0
            if np.any(voiced_frames):
                mean_pitch = np.mean(pitches[voiced_frames])
                
                # Normalize to 0-1 range (typical range is 100-300 Hz)
                return min(max((mean_pitch - 100) / 200, 0.0), 1.0)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating pitch: {str(e)}")
            return 0.5
    
    def _calculate_fluency(self, y: np.ndarray) -> float:
        """
        Calculate speech fluency score.
        """
        try:
            # Get onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate)
            
            # Find onset frames
            onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env)
            
            # Calculate intervals between onsets
            if len(onset_frames) > 1:
                intervals = np.diff(onset_frames)
                
                # Calculate regularity of intervals
                interval_std = np.std(intervals)
                interval_mean = np.mean(intervals)
                
                # Calculate coefficient of variation
                cv = interval_std / interval_mean if interval_mean > 0 else 0
                
                # Convert to fluency score (lower CV = more fluent)
                return 1.0 - min(cv, 1.0)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating fluency: {str(e)}")
            return 0.5
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """
        Return default metrics when analysis fails.
        """
        return {
            "speech_rate": 0.5,
            "volume": 0.5,
            "pitch": 0.5,
            "fluency": 0.5
        }

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