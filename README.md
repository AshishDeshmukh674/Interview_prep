# AI Interview Assistant

An AI-powered interview system that evaluates candidates based on their responses and non-verbal cues during video interviews.

## Features

- Resume parsing and analysis
- Real-time face and eye contact analysis
- Response evaluation using Groq LLM
- Comprehensive feedback on both verbal and non-verbal aspects
- Modern web interface for easy interaction

## Prerequisites

- Python 3.8 or higher
- Webcam for video interviews
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd interview_ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the FastAPI server:
```bash
cd interview_ai
uvicorn backend.main:app --reload
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Follow the on-screen instructions:
   - Upload your resume (PDF or DOCX)
   - Allow camera access when prompted
   - Answer the interview questions
   - Submit your responses
   - View detailed feedback

## Project Structure

```
interview_ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── interview_manager.py # Interview flow management
│   ├── face_analyzer.py     # Face and eye contact analysis
│   ├── resume_parser.py     # Resume parsing
│   ├── interview_evaluator.py # Response evaluation
│   └── templates/
│       └── index.html       # Frontend interface
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

- `GET /`: Home page
- `POST /upload_resume/`: Upload and parse resume
- `POST /process_response/`: Process interview response and video
- `POST /end_interview/`: End interview and get final evaluation
- `GET /health/`: Health check endpoint

## Evaluation Metrics

The system evaluates candidates based on:

1. Face Analysis:
   - Face detection rate
   - Eye contact rate
   - Confidence score

2. Response Evaluation:
   - Technical accuracy
   - Communication clarity
   - Problem-solving approach
   - Relevance to role
   - Areas for improvement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 