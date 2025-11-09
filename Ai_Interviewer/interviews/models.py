from django.db import models

# Create your models here.
from accounts.models import User

class Interview(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_interviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    duration_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class EvaluationCriteria(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='criteria')
    criterion_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    weight = models.IntegerField(default=1)  # Importance weight
    
    def __str__(self):
        return f"{self.interview.title} - {self.criterion_name}"

class ExpectedSkill(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='expected_skills')
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.interview.title} - {self.skill_name}"

class RoleResponsibility(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='responsibilities')
    responsibility = models.TextField()
    
    def __str__(self):
        return f"{self.interview.title} - Responsibility"

class InterviewAttempt(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='attempts')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.candidate.username} - {self.interview.title}"

class InterviewResult(models.Model):
    attempt = models.OneToOneField(InterviewAttempt, on_delete=models.CASCADE, related_name='result')
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    technical_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    communication_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    problem_solving_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    feedback = models.TextField()
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    recommendation = models.CharField(max_length=50)  # e.g., "Highly Recommended", "Not Recommended"
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result for {self.attempt}"
