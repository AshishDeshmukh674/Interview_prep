from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store sessions in memory (replace with proper database in production)
sessions = set()

@app.post("/api/start-session")
async def start_session():
    """Initialize a new session"""
    session_id = str(uuid4())
    sessions.add(session_id)  # Store session
    return {"session_id": session_id}

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile,
    x_session_id: str = Header(None, alias="X-Session-ID")
):
    if not x_session_id:
        raise HTTPException(status_code=401, detail="No session ID provided")
    
    if x_session_id not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    
    # Process the resume
    # ... existing code ... 
    return {"status": "success"} 