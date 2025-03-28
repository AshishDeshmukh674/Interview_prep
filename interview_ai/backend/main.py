from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import os
import json
import uuid
import asyncio
from datetime import datetime
from .resume_parser import ResumeParser
from .interview_session import InterviewSession
from .interview_evaluator import InterviewEvaluator
from .face_analyzer import FaceAnalyzer
from .voice_analyzer import VoiceAnalyzer
import cv2
import numpy as np
from .interview_manager import InterviewManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Interview Assistant")

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active interview sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize managers
interview_manager = InterviewManager()
resume_parser = ResumeParser()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse resume
        resume_data = resume_parser.parse_resume(content)
        
        # Start interview session
        interview_data = interview_manager.start_interview(resume_data)
        
        return {
            "status": "success",
            "message": "Resume uploaded and parsed successfully",
            "data": interview_data
        }
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start-interview")
async def start_interview(resume_data: dict):
    try:
        session_id = str(uuid.uuid4())
        active_sessions[session_id] = {
            "resume_data": resume_data,
            "current_question": None,
            "questions_asked": [],
            "responses": [],
            "feedback": [],
            "status": "active"
        }
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.close(code=4000, reason="Invalid session ID")
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "frame":
                # Process video frame for face detection
                frame_data = np.frombuffer(data["frame"], dtype=np.uint8)
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                # Calculate metrics
                metrics = {
                    "face_detected": len(faces) > 0,
                    "eye_contact": True if len(faces) > 0 else False,
                    "confidence_score": 0.8 if len(faces) > 0 else 0.2
                }
                
                await websocket.send_json({
                    "type": "metrics",
                    "data": metrics
                })
            
            elif data["type"] == "response":
                # Process interview response
                response = data["response"]
                active_sessions[session_id]["responses"].append(response)
                
                # Generate feedback
                feedback = {
                    "clarity": 0.85,
                    "relevance": 0.9,
                    "technical_accuracy": 0.8,
                    "suggestions": ["Good explanation", "Consider adding more examples"]
                }
                
                active_sessions[session_id]["feedback"].append(feedback)
                await websocket.send_json({
                    "type": "feedback",
                    "data": feedback
                })
    
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        await websocket.close()

@app.get("/api/interview-status/{session_id}")
async def get_interview_status(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": active_sessions[session_id]["status"],
        "questions_asked": len(active_sessions[session_id]["questions_asked"]),
        "responses_received": len(active_sessions[session_id]["responses"])
    }

@app.get("/api/interview-feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    overall_feedback = {
        "technical_score": sum(f["technical_accuracy"] for f in session["feedback"]) / len(session["feedback"]),
        "communication_score": sum(f["clarity"] for f in session["feedback"]) / len(session["feedback"]),
        "eye_contact_score": 0.8,  # Placeholder for now
        "strengths": ["Clear communication", "Good technical knowledge"],
        "areas_for_improvement": ["Add more specific examples", "Maintain consistent eye contact"],
        "recommendations": ["Practice with more complex scenarios", "Focus on implementation details"]
    }
    
    return {"feedback": overall_feedback}

@app.get("/health/")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "healthy", "message": "Service is running"}

@app.post("/api/process-response")
async def process_response(response: str, video: UploadFile = File(...)):
    """
    Process the candidate's response and video.
    """
    try:
        # Read video content
        video_content = await video.read()
        
        # Process response
        result = await interview_manager.process_response(response, video_content)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview-status")
async def get_interview_status():
    """
    Get the current status of the interview.
    """
    try:
        return {
            "status": "success",
            "data": {
                "current_question": interview_manager.current_question,
                "question_index": interview_manager.current_question_index,
                "total_questions": len(interview_manager.questions),
                "responses_count": len(interview_manager.responses)
            }
        }
    except Exception as e:
        logger.error(f"Error getting interview status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup function to remove old sessions
@app.on_event("startup")
async def startup_event():
    # Create required directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup temporary files
    if os.path.exists("uploads"):
        for file in os.listdir("uploads"):
            os.remove(os.path.join("uploads", file))
