from django.db.models import Avg
from django.shortcuts import render
from projects.models import Project


def homepage(request):
    return render(
        request,
        "home/homepage.html",
        {
            "top_projects": Project.objects.annotate(
                avg_rating=Avg("ratings__value")
            ).order_by("-avg_rating")[:5],
            "latest_projects": Project.objects.order_by("-created_at")[:5],
        },
    )
