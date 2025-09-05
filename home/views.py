from django.db.models import Avg
from django.shortcuts import render
from projects.models import Project

def homepage(request):
    # top 5 projects by average rating
    top_projects = Project.objects.annotate(avg_rating=Avg("ratings__value")).order_by("-avg_rating")[:5]

    # latest 5 projects by created_at
    latest_projects = Project.objects.order_by("-created_at")[:5]

    return render(request, "home/homepage.html", {
        "top_projects": top_projects,
        "latest_projects": latest_projects,
    })