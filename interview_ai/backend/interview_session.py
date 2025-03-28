import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from .interview_evaluator import InterviewEvaluator
from .face_analyzer import FaceAnalyzer
from .voice_analyzer import VoiceAnalyzer

logger = logging.getLogger(__name__)

class InterviewSession:
    def __init__(self, session_id: str, duration_minutes: int):
        self.session_id = session_id
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.is_active = True
        self.current_question_index = 0
        self.questions: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.resume_data: Optional[Dict[str, Any]] = None
        
        # Initialize analyzers
        self.evaluator = InterviewEvaluator()
        self.face_analyzer = FaceAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        
    async def start_session(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new interview session with the given resume data.
        """
        try:
            self.resume_data = resume_data
            self.questions = await self._generate_questions()
            
            return {
                "session_id": self.session_id,
                "duration_minutes": self.duration_minutes,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "first_question": self.questions[0] if self.questions else None,
                "total_questions": len(self.questions)
            }
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            raise
    
    async def process_response(
        self,
        response: str,
        video_data: bytes
    ) -> Dict[str, Any]:
        """
        Process a candidate's response and video data.
        """
        try:
            if not self.is_active:
                return {"status": "error", "message": "Session has ended"}
            
            # Check if time is up
            if datetime.now() >= self.end_time:
                self.is_active = False
                return {"status": "complete", "message": "Time is up"}
            
            # Analyze face metrics
            face_metrics = await self.face_analyzer.analyze(video_data)
            
            # Analyze voice metrics
            voice_metrics = await self.voice_analyzer.analyze(video_data)
            
            # Evaluate response
            evaluation = await self.evaluator.evaluate_response(
                response,
                self.questions[self.current_question_index],
                self.resume_data
            )
            
            # Store response and metrics
            self.responses.append({
                "question": self.questions[self.current_question_index],
                "response": response,
                "face_metrics": face_metrics,
                "voice_metrics": voice_metrics,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to next question
            self.current_question_index += 1
            
            # Check if interview is complete
            if self.current_question_index >= len(self.questions):
                self.is_active = False
                return {
                    "status": "complete",
                    "message": "Interview completed",
                    "next_question": None
                }
            
            return {
                "status": "success",
                "message": "Response processed",
                "next_question": self.questions[self.current_question_index],
                "metrics": {
                    "face": face_metrics,
                    "voice": voice_metrics,
                    "evaluation": evaluation
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_final_feedback(self) -> Dict[str, Any]:
        """
        Generate final feedback for the interview session.
        """
        try:
            if not self.responses:
                return {
                    "status": "error",
                    "message": "No responses recorded"
                }
            
            # Calculate overall metrics
            overall_face_metrics = self._calculate_overall_face_metrics()
            overall_voice_metrics = self._calculate_overall_voice_metrics()
            overall_evaluation = self._calculate_overall_evaluation()
            
            return {
                "status": "success",
                "session_summary": {
                    "duration": self.duration_minutes,
                    "total_questions": len(self.questions),
                    "questions_answered": len(self.responses),
                    "completion_time": (self.end_time - self.start_time).total_seconds()
                },
                "metrics": {
                    "face": overall_face_metrics,
                    "voice": overall_voice_metrics,
                    "evaluation": overall_evaluation
                },
                "responses": self.responses
            }
            
        except Exception as e:
            logger.error(f"Error generating final feedback: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _generate_questions(self) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on resume data.
        """
        try:
            # Generate questions using the evaluator
            questions = await self.evaluator.generate_questions(self.resume_data)
            return questions
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise
    
    def _calculate_overall_face_metrics(self) -> Dict[str, float]:
        """
        Calculate overall face metrics from all responses.
        """
        if not self.responses:
            return {}
        
        total_metrics = {
            "eye_contact_rate": 0.0,
            "face_detection_rate": 0.0,
            "head_position_score": 0.0
        }
        
        for response in self.responses:
            face_metrics = response.get("face_metrics", {})
            for metric in total_metrics:
                if metric in face_metrics:
                    total_metrics[metric] += face_metrics[metric]
        
        # Calculate averages
        num_responses = len(self.responses)
        for metric in total_metrics:
            total_metrics[metric] /= num_responses
        
        return total_metrics
    
    def _calculate_overall_voice_metrics(self) -> Dict[str, float]:
        """
        Calculate overall voice metrics from all responses.
        """
        if not self.responses:
            return {}
        
        total_metrics = {
            "speech_rate": 0.0,
            "volume": 0.0,
            "pitch": 0.0,
            "fluency": 0.0
        }
        
        for response in self.responses:
            voice_metrics = response.get("voice_metrics", {})
            for metric in total_metrics:
                if metric in voice_metrics:
                    total_metrics[metric] += voice_metrics[metric]
        
        # Calculate averages
        num_responses = len(self.responses)
        for metric in total_metrics:
            total_metrics[metric] /= num_responses
        
        return total_metrics
    
    def _calculate_overall_evaluation(self) -> Dict[str, Any]:
        """
        Calculate overall evaluation metrics from all responses.
        """
        if not self.responses:
            return {}
        
        total_score = 0.0
        strengths = set()
        areas_for_improvement = set()
        recommendations = set()
        
        for response in self.responses:
            evaluation = response.get("evaluation", {})
            total_score += evaluation.get("score", 0.0)
            
            # Collect unique strengths
            for strength in evaluation.get("strengths", []):
                strengths.add(strength)
            
            # Collect unique areas for improvement
            for area in evaluation.get("areas_for_improvement", []):
                areas_for_improvement.add(area)
            
            # Collect unique recommendations
            for recommendation in evaluation.get("recommendations", []):
                recommendations.add(recommendation)
        
        # Calculate average score
        num_responses = len(self.responses)
        average_score = total_score / num_responses if num_responses > 0 else 0.0
        
        return {
            "score": average_score,
            "strengths": list(strengths),
            "areas_for_improvement": list(areas_for_improvement),
            "recommendations": list(recommendations)
        } 