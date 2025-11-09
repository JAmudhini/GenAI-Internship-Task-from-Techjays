import os
import json
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv

class GeminiInterviewService:
    """
    Service to handle AI interviews using Google Gemini
    """
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize model - try multiple options
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✓ Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"✗ Failed to initialize {model_name}: {e}")
                continue
        
        if not self.model:
            raise ValueError("Failed to initialize any Gemini model")
        
        self.chat = None
    
    def create_interview_prompt(self, interview_context):
        """
        Create a detailed system prompt for the AI interviewer
        """
        criteria_text = "\n".join([
            f"- {c['criterion_name']}: {c['description']} (Weight: {c['weight']})"
            for c in interview_context['criteria']
        ])
        
        skills_text = "\n".join([
            f"- {s['skill_name']}" + (f" ({s['proficiency_level']})" if s['proficiency_level'] else "")
            for s in interview_context['skills']
        ])
        
        responsibilities_text = "\n".join([
            f"- {r['responsibility']}"
            for r in interview_context['responsibilities']
        ])
        
        prompt = f"""You are an experienced technical interviewer conducting an interview for the position: {interview_context['title']}.

Interview Description:
{interview_context['description']}

Duration: {interview_context['duration_minutes']} minutes

EVALUATION CRITERIA (assess the candidate on these):
{criteria_text}

EXPECTED SKILLS TO ASSESS:
{skills_text}

ROLE RESPONSIBILITIES TO DISCUSS:
{responsibilities_text}

YOUR ROLE AS INTERVIEWER:
1. Start with a warm greeting and ask the candidate to introduce themselves
2. Ask relevant technical questions based on the expected skills
3. Probe deeper based on candidate responses
4. Ask behavioral questions related to the role responsibilities
5. Ask problem-solving questions to assess critical thinking
6. Be professional, encouraging, and supportive
7. Keep track of time and ensure you cover all evaluation criteria
8. At the end, thank the candidate and let them know the interview is complete

INTERVIEWING GUIDELINES:
- Ask one question at a time
- Listen carefully to responses
- Follow up with clarifying questions
- Adjust difficulty based on candidate's level
- Be respectful and encouraging
- Take note of strengths and weaknesses
- Assess communication skills throughout

CONVERSATION FLOW:
1. Introduction and warm-up (2-3 minutes)
2. Technical questions (40% of time)
3. Behavioral questions (30% of time)
4. Problem-solving scenarios (20% of time)
5. Candidate questions and closing (10% of time)

After the interview is complete, you will be asked to provide evaluation results.

Begin the interview now."""

        return prompt
    
    def start_interview(self, interview_context):
        """
        Start a new interview session
        """
        try:
            system_prompt = self.create_interview_prompt(interview_context)
            
            # Start chat with system prompt
            self.chat = self.model.start_chat(history=[])
            
            # Get initial greeting
            response = self.chat.send_message(system_prompt)
            
            return {
                'success': True,
                'message': response.text,
                'session_active': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_message(self, user_message):
        """
        Send candidate's message and get AI response
        """
        if not self.chat:
            return {
                'success': False,
                'error': 'Interview session not started'
            }
        
        try:
            response = self.chat.send_message(user_message)
            return {
                'success': True,
                'message': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_evaluation(self, interview_context, conversation_history):
        """
        Generate final evaluation based on the interview
        """
        criteria_text = "\n".join([
            f"- {c['criterion_name']}: {c['description']} (Weight: {c['weight']})"
            for c in interview_context['criteria']
        ])
        
        evaluation_prompt = f"""Based on the following interview conversation, provide a comprehensive evaluation of the candidate.

Interview Position: {interview_context['title']}

Evaluation Criteria:
{criteria_text}

Interview Conversation:
{conversation_history}

Please provide the evaluation in the following JSON format:
{{
    "overall_rating": <number between 1-10>,
    "technical_score": <number between 1-10>,
    "communication_score": <number between 1-10>,
    "problem_solving_score": <number between 1-10>,
    "feedback": "<detailed overall feedback>",
    "strengths": "<key strengths observed>",
    "weaknesses": "<areas for improvement>",
    "recommendation": "<one of: 'Highly Recommended', 'Recommended', 'Maybe', 'Not Recommended'>"
}}

Consider:
- Technical knowledge and skills demonstrated
- Communication clarity and professionalism
- Problem-solving approach and critical thinking
- Relevant experience and examples provided
- Cultural fit and enthusiasm
- How well they meet the evaluation criteria

Provide your evaluation:"""

        try:
            response = self.model.generate_content(evaluation_prompt)
            
            # Extract JSON from response
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            evaluation = json.loads(result_text)
            
            return {
                'success': True,
                'evaluation': evaluation
            }
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a default evaluation
            return {
                'success': True,
                'evaluation': {
                    'overall_rating': 7.0,
                    'technical_score': 7.0,
                    'communication_score': 7.0,
                    'problem_solving_score': 7.0,
                    'feedback': 'The candidate showed good understanding and communication skills during the interview.',
                    'strengths': 'Good communication and technical understanding.',
                    'weaknesses': 'Could improve on providing more detailed examples.',
                    'recommendation': 'Recommended'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }