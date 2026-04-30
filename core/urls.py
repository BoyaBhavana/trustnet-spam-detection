from django.urls import path
from .views import (
    home, analyze, login_view, register_view, logout_view,
    history, reports, profile_check, api_info, export_csv,
    batch_analysis
)

urlpatterns = [
    path('', home, name='home'),
    path('analyze/', analyze, name='analyze'),

    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('history/', history, name='history'),
    path('reports/', reports, name='reports'),
    path('profile-check/', profile_check, name='profile_check'),
    path('api-info/', api_info, name='api_info'),
    path('export/', export_csv, name='export'),
    path('batch-analysis/', batch_analysis, name='batch_analysis'),
]