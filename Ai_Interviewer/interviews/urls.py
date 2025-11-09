from django.urls import path
from . import views

urlpatterns = [
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/create/', views.create_interview, name='create_interview'),
    path('hr/edit/<int:interview_id>/', views.edit_interview, name='edit_interview'),
    path('hr/delete/<int:interview_id>/', views.delete_interview, name='delete_interview'),
    path('hr/results/<int:interview_id>/', views.view_results, name='view_results'),
    path('hr/add-criteria/<int:interview_id>/', views.add_criteria, name='add_criteria'),
    path('hr/add-skill/<int:interview_id>/', views.add_skill, name='add_skill'),
    path('hr/add-responsibility/<int:interview_id>/', views.add_responsibility, name='add_responsibility'),
    
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/start/<int:interview_id>/', views.start_interview, name='start_interview'),
    path('candidate/session/<int:attempt_id>/', views.interview_session, name='interview_session'),
    path('candidate/result/<int:attempt_id>/', views.view_my_result, name='view_my_result'),
]
