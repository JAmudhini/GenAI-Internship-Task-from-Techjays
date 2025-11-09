from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Interview, InterviewAttempt, InterviewResult, EvaluationCriteria, ExpectedSkill, RoleResponsibility
from .forms import InterviewForm, EvaluationCriteriaForm, ExpectedSkillForm, RoleResponsibilityForm
import uuid
import os

@login_required
def hr_dashboard(request):
    if request.user.user_type != 'HR':
        return redirect('candidate_dashboard')
    
    interviews = Interview.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Get statistics
    total_interviews = interviews.count()
    active_interviews = interviews.filter(status='ACTIVE').count()
    total_attempts = InterviewAttempt.objects.filter(interview__created_by=request.user).count()
    
    context = {
        'interviews': interviews,
        'total_interviews': total_interviews,
        'active_interviews': active_interviews,
        'total_attempts': total_attempts,
    }
    return render(request, 'interviews/hr_dashboard.html', context)

@login_required
def create_interview(request):
    if request.user.user_type != 'HR':
        messages.error(request, 'Only HR can create interviews')
        return redirect('candidate_dashboard')
    
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.created_by = request.user
            interview.save()
            messages.success(request, 'Interview created successfully! Now add criteria, skills, and responsibilities.')
            return redirect('edit_interview', interview_id=interview.id)
    else:
        form = InterviewForm()
    
    return render(request, 'interviews/create_interview.html', {'form': form})

@login_required
def edit_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview updated successfully!')
            return redirect('edit_interview', interview_id=interview.id)
    else:
        form = InterviewForm(instance=interview)
    
    criteria = interview.criteria.all()
    skills = interview.expected_skills.all()
    responsibilities = interview.responsibilities.all()
    
    context = {
        'interview': interview,
        'form': form,
        'criteria': criteria,
        'skills': skills,
        'responsibilities': responsibilities,
        'criteria_form': EvaluationCriteriaForm(),
        'skill_form': ExpectedSkillForm(),
        'responsibility_form': RoleResponsibilityForm(),
    }
    return render(request, 'interviews/edit_interview.html', context)

@login_required
def add_criteria(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    
    if request.method == 'POST':
        form = EvaluationCriteriaForm(request.POST)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.interview = interview
            criteria.save()
            messages.success(request, 'Evaluation criteria added!')
    
    return redirect('edit_interview', interview_id=interview.id)

@login_required
def add_skill(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ExpectedSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.interview = interview
            skill.save()
            messages.success(request, 'Expected skill added!')
    
    return redirect('edit_interview', interview_id=interview.id)

@login_required
def add_responsibility(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    
    if request.method == 'POST':
        form = RoleResponsibilityForm(request.POST)
        if form.is_valid():
            responsibility = form.save(commit=False)
            responsibility.interview = interview
            responsibility.save()
            messages.success(request, 'Role responsibility added!')
    
    return redirect('edit_interview', interview_id=interview.id)

@login_required
def delete_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    interview.delete()
    messages.success(request, 'Interview deleted successfully!')
    return redirect('hr_dashboard')

@login_required
def view_results(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, created_by=request.user)
    attempts = InterviewAttempt.objects.filter(interview=interview).select_related('candidate', 'result').order_by('-started_at')
    
    context = {
        'interview': interview,
        'attempts': attempts,
    }
    return render(request, 'interviews/view_results.html', context)

@login_required
def candidate_dashboard(request):
    if request.user.user_type != 'CANDIDATE':
        return redirect('hr_dashboard')
    
    available_interviews = Interview.objects.filter(status='ACTIVE').order_by('-created_at')
    my_attempts = InterviewAttempt.objects.filter(candidate=request.user).select_related('interview').order_by('-started_at')
    
    context = {
        'available_interviews': available_interviews,
        'my_attempts': my_attempts,
    }
    return render(request, 'interviews/candidate_dashboard.html', context)

@login_required
def start_interview(request, interview_id):
    if request.user.user_type != 'CANDIDATE':
        messages.error(request, 'Only candidates can take interviews')
        return redirect('hr_dashboard')
    
    interview = get_object_or_404(Interview, id=interview_id, status='ACTIVE')
    
    # Create interview attempt
    attempt = InterviewAttempt.objects.create(
        interview=interview,
        candidate=request.user,
        status='IN_PROGRESS',
        started_at=timezone.now(),
        session_id=str(uuid.uuid4())
    )
    
    return redirect('interview_session', attempt_id=attempt.id)

@login_required
def interview_session(request, attempt_id):
    attempt = get_object_or_404(InterviewAttempt, id=attempt_id, candidate=request.user)
    interview = attempt.interview
    
    # Prepare interview context for Gemini
    criteria = interview.criteria.all()
    skills = interview.expected_skills.all()
    responsibilities = interview.responsibilities.all()
    
    context = {
        'attempt': attempt,
        'interview': interview,
        'criteria': criteria,
        'skills': skills,
        'responsibilities': responsibilities,
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),  # Add this line
    }
    return render(request, 'interviews/interview_session.html', context)

@login_required
def view_my_result(request, attempt_id):
    attempt = get_object_or_404(InterviewAttempt, id=attempt_id, candidate=request.user)
    
    try:
        result = attempt.result
    except InterviewResult.DoesNotExist:
        messages.error(request, 'Results not available yet.')
        return redirect('candidate_dashboard')
    
    context = {
        'attempt': attempt,
        'result': result,
    }
    return render(request, 'interviews/view_my_result.html', context)
