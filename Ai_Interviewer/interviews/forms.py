from django import forms
from .models import Interview, EvaluationCriteria, ExpectedSkill, RoleResponsibility

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['title', 'description', 'duration_minutes', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Python Developer Interview'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the interview...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 120}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class EvaluationCriteriaForm(forms.ModelForm):
    class Meta:
        model = EvaluationCriteria
        fields = ['criterion_name', 'description', 'weight']
        widgets = {
            'criterion_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technical Knowledge'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

class ExpectedSkillForm(forms.ModelForm):
    class Meta:
        model = ExpectedSkill
        fields = ['skill_name', 'proficiency_level']
        widgets = {
            'skill_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, Django, REST API'}),
            'proficiency_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Expert, Intermediate'}),
        }

class RoleResponsibilityForm(forms.ModelForm):
    class Meta:
        model = RoleResponsibility
        fields = ['responsibility']
        widgets = {
            'responsibility': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe a key responsibility...'}),
        }
