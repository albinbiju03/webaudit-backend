from django.urls import path
from .views import analyze_website, backend_home, health_check, ai_insights

urlpatterns = [
    path("", backend_home, name="backend_home"),
    path("api/health/", health_check, name="health"),
    path("api/analyze/", analyze_website, name="analyze"),
    path("api/ai-insights/", ai_insights, name="ai_insights"),
]
