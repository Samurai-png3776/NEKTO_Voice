from django.shortcuts import render, get_object_or_404
from .models import Title, Episode

def public_home(request):
    titles = Title.objects.all().order_by('-created_at')
    return render(request, 'core/public_home.html', {'titles': titles})

def public_title_detail(request, title_id):
    title = get_object_or_404(Title, id=title_id)
    episodes = title.episodes.all().order_by('number')
    return render(request, 'core/public_title.html', {'title': title, 'episodes': episodes})

def team_dashboard(request):
    titles = Title.objects.all()
    return render(request, 'core/dashboard.html', {'titles': titles})