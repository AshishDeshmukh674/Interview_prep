import logging
from typing import Dict, Any, List
from .resume_parser import extract_resume_data
from .face_analyzer import analyze_face
from .interview_evaluator import evaluate_response
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewManager:
    def __init__(self):
        self.current_interview = None
        self.responses = []
        self.face_analysis_results = []
        self.current_question = None
        self.resume_data = None
        self.questions = []
        self.current_question_index = 0
        
    def start_interview(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new interview session with resume data.
        """
        try:
            self.resume_data = resume_data
            self.current_interview = {
                "start_time": datetime.now().isoformat(),
                "resume_data": resume_data,
                "status": "in_progress"
            }
            
            # Generate initial questions based on resume
            self.questions = self._generate_questions(resume_data)
            self.current_question = self.questions[0] if self.questions else None
            self.current_question_index = 0
            
            return {
                "interview_id": id(self.current_interview),
                "questions": self.questions,
                "current_question": self.current_question,
                "start_time": self.current_interview["start_time"]
            }
        except Exception as e:
            logger.error(f"Error starting interview: {str(e)}")
            raise
            
    async def process_response(self, response: str, video_data: bytes) -> Dict[str, Any]:
        """
        Process the candidate's response and video.
        """
        try:
            if not self.current_interview:
                raise ValueError("No active interview session")

            # Analyze face
            face_analysis = analyze_face(video_data)
            if "error" in face_analysis:
                logger.warning(f"Face analysis warning: {face_analysis['error']}")
            self.face_analysis_results.append(face_analysis)
            
            # Evaluate response
            response_evaluation = await evaluate_response(
                response,
                self.current_question if self.current_question else "",
                self.resume_data if self.resume_data else {}
            )
            
            # Store response
            result = {
                "response": response,
                "face_analysis": {
                    "face_detection_rate": face_analysis.get("face_detection_rate", 0.0),
                    "eye_contact_rate": face_analysis.get("eye_contact_rate", 0.0),
                    "confidence_score": face_analysis.get("confidence_score", 0.0),
                    "frame_count": face_analysis.get("frame_count", 0),
                    "detected_frames": face_analysis.get("detected_frames", 0),
                    "error": face_analysis.get("error", None)
                },
                "response_evaluation": response_evaluation,
                "timestamp": datetime.now().isoformat()
            }
            self.responses.append(result)
            
            # Move to next question if available
            self.current_question_index += 1
            if self.current_question_index < len(self.questions):
                self.current_question = self.questions[self.current_question_index]
            else:
                self.current_question = None
            
            return {
                "status": "success",
                "result": result,
                "next_question": self.current_question,
                "interview_progress": {
                    "current_question": self.current_question_index,
                    "total_questions": len(self.questions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "result": {
                    "face_analysis": {
                        "face_detection_rate": 0.0,
                        "eye_contact_rate": 0.0,
                        "confidence_score": 0.0,
                        "frame_count": 0,
                        "detected_frames": 0,
                        "error": str(e)
                    },
                    "response_evaluation": {
                        "score": 0,
                        "strengths": [],
                        "areas_for_improvement": ["Unable to evaluate response due to error"],
                        "detailed_feedback": f"Error processing response: {str(e)}",
                        "recommendations": ["Please try again"]
                    }
                }
            }
            
    def end_interview(self) -> Dict[str, Any]:
        """
        End the interview and generate final evaluation.
        """
        try:
            if not self.current_interview:
                raise ValueError("No active interview session")
                
            # Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics()
            
            # Generate final evaluation
            final_evaluation = self._generate_final_evaluation(overall_metrics)
            
            # Update interview status
            self.current_interview.update({
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                "responses": self.responses,
                "face_analysis_results": self.face_analysis_results,
                "overall_metrics": overall_metrics,
                "final_evaluation": final_evaluation
            })
            
            return {
                "interview_id": id(self.current_interview),
                "overall_metrics": overall_metrics,
                "final_evaluation": final_evaluation,
                "end_time": self.current_interview["end_time"]
            }
        except Exception as e:
            logger.error(f"Error ending interview: {str(e)}")
            raise
            
    def _generate_questions(self, resume_data: Dict[str, Any]) -> List[str]:
        """
        Generate interview questions based on resume data.
        """
        # TODO: Implement question generation using Groq LLM
        return [
            "Tell me about your experience with Python programming.",
            "What projects have you worked on that you're most proud of?",
            "How do you handle tight deadlines and multiple priorities?"
        ]
        
    def _calculate_overall_metrics(self) -> Dict[str, float]:
        """
        Calculate overall interview metrics.
        """
        if not self.face_analysis_results:
            return {}
            
        # Calculate averages
        avg_face_detection = sum(r["face_detection_rate"] for r in self.face_analysis_results) / len(self.face_analysis_results)
        avg_eye_contact = sum(r["eye_contact_rate"] for r in self.face_analysis_results) / len(self.face_analysis_results)
        avg_confidence = sum(r["confidence_score"] for r in self.face_analysis_results) / len(self.face_analysis_results)
        
        return {
            "face_detection_rate": avg_face_detection,
            "eye_contact_rate": avg_eye_contact,
            "confidence_score": avg_confidence
        }
        
    def _generate_final_evaluation(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate final interview evaluation.
        """
        # TODO: Implement final evaluation generation using Groq LLM
        return {
            "overall_score": (metrics.get("face_detection_rate", 0) + 
                            metrics.get("eye_contact_rate", 0) + 
                            metrics.get("confidence_score", 0)) / 3,
            "strengths": ["Good communication", "Technical knowledge"],
            "areas_for_improvement": ["Eye contact", "Response structure"],
            "recommendations": ["Practice maintaining eye contact", "Structure responses better"]
        } 