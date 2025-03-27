from setuptools import setup, find_packages

setup(
    name="interview_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "pytest==7.4.3",
        "pdfplumber==0.10.3",
        "python-docx==1.0.1",
        "PyPDF2==3.0.1",
        "groq==0.4.2",
    ],
) 