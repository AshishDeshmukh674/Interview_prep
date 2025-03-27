import logging
import os
from typing import Dict, Any
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    client = groq.Client(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    raise

def evaluate_response(response: str, current_question: str, resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate an interview response using the Groq LLM.
    
    Args:
        response: The candidate's response
        current_question: The current interview question
        resume_data: The candidate's resume data
        
    Returns:
        Dict containing the evaluation results
    """
    try:
        # Prepare context from resume data
        context = _prepare_context(resume_data)
        
        # Generate evaluation prompt
        prompt = _generate_evaluation_prompt(context, current_question, response)
        
        # Get evaluation from Groq
        evaluation = _get_groq_evaluation(prompt)
        
        # Parse and structure the evaluation
        return _parse_evaluation(evaluation)
        
    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}")
        return {
            "score": 0,
            "strengths": [],
            "areas_for_improvement": ["Unable to evaluate response due to error"],
            "detailed_feedback": f"Error evaluating response: {str(e)}",
            "recommendations": ["Please try again"]
        }

def _prepare_context(resume_data: Dict[str, Any]) -> str:
    """
    Prepare context from resume data for the evaluation.
    """
    context_parts = []
    
    # Add contact info
    if resume_data.get("contact_info"):
        contact = resume_data["contact_info"]
        context_parts.append(f"Candidate: {contact.get('name', 'Unknown')}")
        context_parts.append(f"Email: {contact.get('email', 'Not provided')}")
        context_parts.append(f"Location: {contact.get('location', 'Not provided')}")
    
    # Add education
    if resume_data.get("education"):
        context_parts.append("\nEducation:")
        for edu in resume_data["education"]:
            context_parts.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})")
    
    # Add experience
    if resume_data.get("experience"):
        context_parts.append("\nExperience:")
        for exp in resume_data["experience"]:
            context_parts.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
            context_parts.append(f"  Duration: {exp.get('duration', 'Not specified')}")
            context_parts.append(f"  Description: {exp.get('description', 'No description provided')}")
    
    # Add skills
    if resume_data.get("skills"):
        context_parts.append("\nSkills:")
        context_parts.append(", ".join(resume_data["skills"]))
    
    return "\n".join(context_parts)

def _generate_evaluation_prompt(context: str, question: str, response: str) -> str:
    """
    Generate the evaluation prompt for the Groq LLM.
    """
    return f"""You are an expert technical interviewer. Based on the candidate's resume and interview response, provide a detailed evaluation.

Candidate's Resume:
{context}

Interview Question:
{question}

Candidate's Response:
{response}

Please evaluate the response considering:
1. Technical accuracy and depth of knowledge
2. Clarity and communication skills
3. Problem-solving approach
4. Relevance to the question and role
5. Areas for improvement

Provide your evaluation in the following format:
Score: [0-100]
Strengths: [List key strengths]
Areas for Improvement: [List areas to improve]
Detailed Feedback: [Detailed analysis of the response]
Recommendations: [Specific recommendations for improvement]

Evaluation:"""

def _get_groq_evaluation(prompt: str) -> str:
    """
    Get evaluation from the Groq LLM.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer providing detailed, constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error getting Groq evaluation: {str(e)}")
        raise

def _parse_evaluation(evaluation: str) -> Dict[str, Any]:
    """
    Parse the Groq evaluation into a structured format.
    """
    try:
        # Initialize result dictionary
        result = {
            "score": 0,
            "strengths": [],
            "areas_for_improvement": [],
            "detailed_feedback": "",
            "recommendations": []
        }
        
        # Split evaluation into lines
        lines = evaluation.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse score
            if line.startswith("Score:"):
                try:
                    result["score"] = int(line.split(":")[1].strip())
                except:
                    pass
                    
            # Parse strengths
            elif line.startswith("Strengths:"):
                current_section = "strengths"
                
            # Parse areas for improvement
            elif line.startswith("Areas for Improvement:"):
                current_section = "areas_for_improvement"
                
            # Parse detailed feedback
            elif line.startswith("Detailed Feedback:"):
                current_section = "detailed_feedback"
                
            # Parse recommendations
            elif line.startswith("Recommendations:"):
                current_section = "recommendations"
                
            # Add content to appropriate section
            elif line.startswith("-"):
                if current_section in ["strengths", "areas_for_improvement", "recommendations"]:
                    result[current_section].append(line[1:].strip())
            elif current_section == "detailed_feedback":
                result["detailed_feedback"] += line + "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing evaluation: {str(e)}")
        return {
            "score": 0,
            "strengths": [],
            "areas_for_improvement": [],
            "detailed_feedback": "Error parsing evaluation",
            "recommendations": []
        }
