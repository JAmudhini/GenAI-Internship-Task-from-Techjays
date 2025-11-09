

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import HRRegistrationForm, CandidateRegistrationForm



def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'HR':
            return redirect('hr_dashboard')
        else:
            return redirect('candidate_dashboard')
    return render(request, 'accounts/home.html')

def register_hr(request):
    if request.method == 'POST':
        form = HRRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'HR account created successfully!')
            return redirect('hr_dashboard')
    else:
        form = HRRegistrationForm()
    return render(request, 'accounts/register_hr.html', {'form': form})

def register_candidate(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Candidate account created successfully!')
            return redirect('candidate_dashboard')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'accounts/register_candidate.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'HR':
                return redirect('hr_dashboard')
            else:
                return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')
