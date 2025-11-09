from django.urls import path
from . import views

urlpatterns = [
    path('start-session/', views.start_interview_session, name='start_session'),
    path('send-message/', views.send_interview_message, name='send_message'),
    path('end-session/', views.end_interview_session, name='end_session'),
    path('submit-result/', views.submit_interview_result, name='submit_result'),
    path('interview-context/<int:attempt_id>/', views.get_interview_context, name='interview_context'),
]