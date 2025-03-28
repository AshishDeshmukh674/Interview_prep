import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
from ..backend.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Interview Assistant" in response.text

def test_read_interview_page():
    response = client.get("/interview")
    assert response.status_code == 200
    assert "Upload Resume" in response.text

def test_upload_resume():
    test_file_path = Path(__file__).parent / "test_data" / "test_resume.pdf"
    if not test_file_path.parent.exists():
        test_file_path.parent.mkdir(parents=True)
    
    # Create a dummy test resume if it doesn't exist
    if not test_file_path.exists():
        with open(test_file_path, "wb") as f:
            f.write(b"Test resume content")
    
    with open(test_file_path, "rb") as f:
        response = client.post(
            "/api/upload-resume",
            files={"resume": ("test_resume.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "parsed_data" in data

@pytest.mark.asyncio
async def test_start_interview():
    resume_data = {
        "name": "John Doe",
        "experience": ["Software Engineer at Tech Corp"],
        "skills": ["Python", "FastAPI", "Machine Learning"]
    }
    
    response = client.post(
        "/api/start-interview",
        json={"resume_data": resume_data}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

@pytest.mark.asyncio
async def test_interview_status():
    # First start an interview
    resume_data = {
        "name": "John Doe",
        "experience": ["Software Engineer"],
        "skills": ["Python"]
    }
    
    start_response = client.post(
        "/api/start-interview",
        json={"resume_data": resume_data}
    )
    
    session_id = start_response.json()["session_id"]
    
    # Then check its status
    response = client.get(f"/api/interview-status/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

@pytest.mark.asyncio
async def test_interview_feedback():
    # First start an interview
    resume_data = {
        "name": "John Doe",
        "experience": ["Software Engineer"],
        "skills": ["Python"]
    }
    
    start_response = client.post(
        "/api/start-interview",
        json={"resume_data": resume_data}
    )
    
    session_id = start_response.json()["session_id"]
    
    # Then get feedback
    response = client.get(f"/api/interview-feedback/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "feedback" in data 