from django.urls import path
from .views import analyze_website, backend_home # (Use your exact function name for the scraper)

urlpatterns = [
    path('', backend_home, name='backend_home'),          # Shows our clean animation
    path('api/analyze/', analyze_website, name='analyze'), # The core API engine for Next.js
]