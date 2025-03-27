from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from typing import Dict, Any
import logging
from .resume_parser import extract_resume_data
from .interview_manager import InterviewManager
from datetime import datetime
import os

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

# Initialize interview manager
interview_manager = InterviewManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and parse a resume file.
    """
    try:
        content = await file.read()
        extracted_data = extract_resume_data(content)
        
        # Start interview with resume data
        interview_result = interview_manager.start_interview(extracted_data)
        
        return {
            "status": "success",
            "resume_data": extracted_data,
            "interview": interview_result,
            "message": "Resume parsed and interview started successfully"
        }
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process resume")

@app.post("/process_response/")
async def process_interview_response(
    response: str = Form(default=...),
    video_file: UploadFile = File(default=...)
) -> Dict[str, Any]:
    """
    Process the candidate's interview response and video.
    """
    try:
        logger.info("Received process_response request")
        logger.info(f"Response text: {response}")
        logger.info(f"Video file name: {video_file.filename}")
        
        # Validate response
        if not response or not response.strip():
            raise HTTPException(
                status_code=400,
                detail="Response text is required"
            )
        
        # Validate video file
        if not video_file or not video_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Video file is required"
            )
            
        if not video_file.content_type or not video_file.content_type.startswith('video/'):
            logger.warning(f"Unexpected content type: {video_file.content_type}")
            # Continue anyway as some browsers might send different content types
        
        # Read video file
        video_content = await video_file.read()
        if not video_content:
            raise HTTPException(
                status_code=400,
                detail="Empty video file received"
            )
        
        # Process response and video
        result = interview_manager.process_response(response, video_content)
        
        if result.get("status") == "error":
            logger.error(f"Error from interview manager: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to process response")
            )
        
        return {
            "status": "success",
            "result": result,
            "message": "Response processed successfully",
            "next_question": result.get("next_question"),
            "interview_progress": result.get("interview_progress", {})
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process response: {str(e)}"
        )

@app.post("/end_interview/")
async def end_interview() -> Dict[str, Any]:
    """
    End the interview and get final evaluation.
    """
    try:
        result = interview_manager.end_interview()
        return {
            "status": "success",
            "result": result,
            "message": "Interview completed successfully"
        }
    except Exception as e:
        logger.error(f"Error ending interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end interview")

@app.get("/health/")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "healthy", "message": "Service is running"}
