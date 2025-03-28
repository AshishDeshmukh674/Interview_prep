from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="interview_ai",
    version="0.1.0",
    author="AI Interview Assistant Team",
    author_email="contact@interview-ai.com",
    description="An AI-powered interview practice platform with real-time feedback",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/interview_ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "interview_ai": [
            "backend/templates/*.html",
            "backend/static/css/*.css",
            "backend/static/js/*.js",
        ]
    },
    entry_points={
        "console_scripts": [
            "interview-ai=interview_ai.run:main",
        ],
    },
) 