from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Comment, Donation, Rating, Report


def project_list(request):
    query = request.GET.get("q")
    if query:
        projects = Project.objects.filter(title__icontains=query)
    else:
        projects = Project.objects.all()
    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    comments = Comment.objects.filter(project=project)
    donations = Donation.objects.filter(project=project)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "comments": comments,
        "donations": donations,
    })

def add_comment(request, project_id):
    if request.method == "POST":
        content = request.POST.get("content")
        project = get_object_or_404(Project, id=project_id)
        Comment.objects.create(user=request.user, project=project, content=content)
        return redirect("projects:project_detail", project_id=project.id)

def donate_to_project(request, project_id):
    if request.method == "POST":
        amount = request.POST.get("amount")
        project = get_object_or_404(Project, id=project_id)
        Donation.objects.create(user=request.user, project=project, amount=amount)
        return redirect("projects:project_detail", project_id=project.id)

def report_project(request, project_id):
    if request.method == "POST":
        reason = request.POST.get("reason")
        project = get_object_or_404(Project, id=project_id)
        Report.objects.create(user=request.user, project=project, reason=reason)
        return redirect("projects:project_detail", project_id=project.id)

def rate_project(request, project_id):
    if request.method == "POST":
        rating = request.POST.get("rating")
        project = get_object_or_404(Project, id=project_id)
        Rating.objects.create(user=request.user, project=project, rating=rating)
        return redirect("projects:project_detail", project_id=project.id)