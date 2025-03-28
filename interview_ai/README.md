# AI Interview Assistant

An AI-powered interview practice platform that provides real-time feedback on technical interviews using advanced computer vision and natural language processing.

## Features

- **Resume-based Question Generation**: Questions are tailored to your experience and technical background
- **Real-time Face Analysis**: Tracks eye contact, face detection, and head position
- **Voice Analysis**: Monitors speech rate, volume, and fluency
- **AI-Powered Response Evaluation**: Provides detailed feedback on your answers
- **WebSocket-based Communication**: Real-time interaction with the interview system
- **Modern UI/UX**: Clean and intuitive interface built with Tailwind CSS

## Prerequisites

- Python 3.8+
- Webcam and microphone
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/interview-ai.git
cd interview-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

1. Start the server:
```bash
uvicorn backend.main:app --reload
```

2. Open your browser and navigate to `http://localhost:8000`

3. Upload your resume and start practicing!

## Project Structure

```
interview_ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── interview_session.py # Interview session management
│   ├── interview_evaluator.py # Response evaluation using Groq
│   ├── face_analyzer.py     # Face analysis using MediaPipe
│   ├── voice_analyzer.py    # Voice analysis using librosa
│   ├── resume_parser.py     # Resume parsing
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       └── interview.html
├── requirements.txt
└── README.md
```

## API Endpoints

- `GET /`: Home page
- `GET /interview`: Interview page
- `POST /api/upload-resume`: Upload and parse resume
- `POST /api/start-interview`: Start a new interview session
- `WebSocket /ws/interview/{session_id}`: Real-time interview communication
- `GET /api/interview-status/{session_id}`: Get interview status
- `GET /api/interview-feedback/{session_id}`: Get final feedback

## Technologies Used

- **Backend**: FastAPI, WebSocket
- **Frontend**: HTML, Tailwind CSS
- **AI/ML**: Groq LLM, MediaPipe, librosa
- **File Processing**: pdfplumber, python-docx
- **Audio Processing**: soundfile

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq for providing the LLM API
- MediaPipe for face analysis capabilities
- FastAPI team for the excellent web framework 