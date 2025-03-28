import os
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

print("Starting imports...")
import numpy as np
print(f"NumPy version: {np.__version__}")

try:
    import cv2
    print("OpenCV imported successfully")
except Exception as e:
    print(f"Error importing OpenCV: {e}")

import uvicorn
from dotenv import load_dotenv

def main():
    """
    Main entry point for the AI Interview Assistant application.
    Loads environment variables and starts the FastAPI server.
    """
    print("Starting main function...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ['GROQ_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following required environment variables are not set:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return
    
    print("Starting FastAPI server...")
    # Start the FastAPI server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 