from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPES = (
        ('HR', 'HR'),
        ('CANDIDATE', 'Candidate'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume = models.FileField(upload_to='resumes/', blank=True)
    skills = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"
