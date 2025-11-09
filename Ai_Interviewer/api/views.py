from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from interviews.models import InterviewAttempt, InterviewResult
from interviews.gemini_service import GeminiInterviewService
import json

# Store active interview sessions (in production, use Redis or similar)
active_sessions = {}

@csrf_exempt
@require_http_methods(["POST"])
def start_interview_session(request):
    """
    Initialize Gemini interview session
    """
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        
        # Get interview attempt and context
        try:
            attempt = InterviewAttempt.objects.select_related('interview').get(id=attempt_id)
        except InterviewAttempt.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Interview attempt not found'
            }, status=404)
        
        interview = attempt.interview
        
        # Prepare interview context
        context = {
            'interview_id': interview.id,
            'title': interview.title,
            'description': interview.description,
            'duration_minutes': interview.duration_minutes,
            'criteria': list(interview.criteria.values('criterion_name', 'description', 'weight')),
            'skills': list(interview.expected_skills.values('skill_name', 'proficiency_level')),
            'responsibilities': list(interview.responsibilities.values('responsibility')),
        }
        
        # Create Gemini service instance
        gemini_service = GeminiInterviewService()
        result = gemini_service.start_interview(context)
        
        if result['success']:
            # Store session
            active_sessions[attempt_id] = {
                'service': gemini_service,
                'context': context,
                'conversation': []
            }
            
            # Add initial message to conversation
            active_sessions[attempt_id]['conversation'].append({
                'role': 'ai',
                'message': result['message']
            })
            
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'attempt_id': attempt_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to start interview session'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_interview_message(request):
    """
    Send message to Gemini and get response
    """
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        user_message = data.get('message')
        
        if attempt_id not in active_sessions:
            return JsonResponse({
                'success': False,
                'error': 'Session not found. Please start the interview first.'
            }, status=404)
        
        session = active_sessions[attempt_id]
        gemini_service = session['service']
        
        # Add user message to conversation
        session['conversation'].append({
            'role': 'user',
            'message': user_message
        })
        
        # Get AI response
        result = gemini_service.send_message(user_message)
        
        if result['success']:
            # Add AI response to conversation
            session['conversation'].append({
                'role': 'ai',
                'message': result['message']
            })
            
            return JsonResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to get response')
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def end_interview_session(request):
    """
    End interview and generate evaluation
    """
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        
        if attempt_id not in active_sessions:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            }, status=404)
        
        session = active_sessions[attempt_id]
        gemini_service = session['service']
        context = session['context']
        conversation = session['conversation']
        
        # Format conversation history
        conversation_text = "\n\n".join([
            f"{'AI Interviewer' if msg['role'] == 'ai' else 'Candidate'}: {msg['message']}"
            for msg in conversation
        ])
        
        # Generate evaluation
        evaluation_result = gemini_service.generate_evaluation(context, conversation_text)
        
        if evaluation_result['success']:
            evaluation = evaluation_result['evaluation']
            
            # Get interview attempt
            attempt = InterviewAttempt.objects.get(id=attempt_id)
            
            # Update attempt status
            attempt.status = 'COMPLETED'
            attempt.completed_at = timezone.now()
            attempt.save()
            
            # Save evaluation results
            result = InterviewResult.objects.create(
                attempt=attempt,
                overall_rating=evaluation.get('overall_rating', 7.0),
                technical_score=evaluation.get('technical_score'),
                communication_score=evaluation.get('communication_score'),
                problem_solving_score=evaluation.get('problem_solving_score'),
                feedback=evaluation.get('feedback', ''),
                strengths=evaluation.get('strengths', ''),
                weaknesses=evaluation.get('weaknesses', ''),
                recommendation=evaluation.get('recommendation', 'Under Review')
            )
            
            # Clean up session
            del active_sessions[attempt_id]
            
            return JsonResponse({
                'success': True,
                'message': 'Interview completed and evaluated',
                'result_id': result.id,
                'evaluation': evaluation
            })
        else:
            return JsonResponse({
                'success': False,
                'error': evaluation_result.get('error', 'Failed to generate evaluation')
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_interview_result(request):
    """
    API endpoint to receive interview results (manual submission)
    """
    try:
        data = json.loads(request.body)
        
        attempt_id = data.get('attempt_id')
        overall_rating = data.get('overall_rating')
        technical_score = data.get('technical_score')
        communication_score = data.get('communication_score')
        problem_solving_score = data.get('problem_solving_score')
        feedback = data.get('feedback', '')
        strengths = data.get('strengths', '')
        weaknesses = data.get('weaknesses', '')
        recommendation = data.get('recommendation', 'Under Review')
        
        # Get the interview attempt
        try:
            attempt = InterviewAttempt.objects.get(id=attempt_id)
        except InterviewAttempt.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Interview attempt not found'
            }, status=404)
        
        # Update attempt status
        attempt.status = 'COMPLETED'
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Create or update result
        result, created = InterviewResult.objects.update_or_create(
            attempt=attempt,
            defaults={
                'overall_rating': overall_rating,
                'technical_score': technical_score,
                'communication_score': communication_score,
                'problem_solving_score': problem_solving_score,
                'feedback': feedback,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendation': recommendation,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Interview result saved successfully',
            'result_id': result.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_interview_context(request, attempt_id):
    """
    API endpoint to get interview context
    """
    try:
        attempt = InterviewAttempt.objects.select_related('interview').get(id=attempt_id)
        interview = attempt.interview
        
        context = {
            'interview_id': interview.id,
            'title': interview.title,
            'description': interview.description,
            'duration_minutes': interview.duration_minutes,
            'criteria': list(interview.criteria.values('criterion_name', 'description', 'weight')),
            'skills': list(interview.expected_skills.values('skill_name', 'proficiency_level')),
            'responsibilities': list(interview.responsibilities.values('responsibility')),
        }
        
        return JsonResponse({
            'success': True,
            'context': context
        })
        
    except InterviewAttempt.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Interview attempt not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)