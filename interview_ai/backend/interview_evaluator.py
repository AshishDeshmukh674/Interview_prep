import logging
import os
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewEvaluator:
    def __init__(self):
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.client = Groq(api_key=api_key)
    
    async def generate_questions(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on resume data.
        """
        try:
            # Prepare prompt
            prompt = f"""
            Based on the following resume data, generate 5-7 relevant technical interview questions.
            Focus on:
            1. Technical skills and experience
            2. Project details and challenges
            3. Problem-solving abilities
            4. System design concepts
            5. Best practices and methodologies
            
            Resume Data:
            {resume_data}
            
            Format each question as a JSON object with:
            - question: The actual question
            - category: Technical area (e.g., "Python", "System Design", "Algorithms")
            - difficulty: Easy/Medium/Hard
            - expected_keywords: List of key terms that should be in the answer
            """
            
            # Generate questions using Groq
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse questions from response
            questions = eval(completion.choices[0].message.content)
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    async def evaluate_response(
        self,
        response: str,
        question: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate's response to an interview question.
        """
        try:
            # Prepare prompt
            prompt = f"""
            Evaluate the following interview response:
            
            Question: {question['question']}
            Category: {question['category']}
            Difficulty: {question['difficulty']}
            Expected Keywords: {', '.join(question['expected_keywords'])}
            
            Candidate's Response:
            {response}
            
            Resume Context:
            {resume_data}
            
            Provide a detailed evaluation in the following JSON format:
            {{
                "score": float (0-1),
                "strengths": List[str],
                "areas_for_improvement": List[str],
                "recommendations": List[str],
                "feedback": str
            }}
            """
            
            # Get evaluation from Groq
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer providing detailed feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse evaluation from response
            evaluation = eval(completion.choices[0].message.content)
            
            # Add metadata
            evaluation.update({
                "timestamp": datetime.now().isoformat(),
                "question_category": question["category"],
                "question_difficulty": question["difficulty"]
            })
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            return {
                "score": 0.5,
                "strengths": [],
                "areas_for_improvement": ["Failed to evaluate response"],
                "recommendations": ["Please try again"],
                "feedback": "An error occurred while evaluating your response.",
                "timestamp": datetime.now().isoformat(),
                "question_category": question.get("category", "Unknown"),
                "question_difficulty": question.get("difficulty", "Unknown")
            }

# Create a global instance of InterviewEvaluator after the class definition
evaluator = InterviewEvaluator()

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
        completion = evaluator.client.chat.completions.create(
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

async def evaluate_response(response: str, question: str, resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a candidate's response to an interview question.
    This is a standalone function that uses the InterviewEvaluator class.
    """
    try:
        # Convert question string to question dict format
        question_dict = {
            "question": question,
            "category": "General",  # Default category
            "difficulty": "Medium",  # Default difficulty
            "expected_keywords": []  # Empty list as we don't have keywords
        }
        
        # Use the evaluator instance to evaluate the response
        evaluation = await evaluator.evaluate_response(response, question_dict, resume_data)
        return evaluation
    except Exception as e:
        logger.error(f"Error in evaluate_response function: {str(e)}")
        return {
            "score": 0.5,
            "strengths": [],
            "areas_for_improvement": ["Failed to evaluate response"],
            "recommendations": ["Please try again"],
            "feedback": "An error occurred while evaluating your response.",
            "timestamp": datetime.now().isoformat(),
            "question_category": "General",
            "question_difficulty": "Medium"
        }
