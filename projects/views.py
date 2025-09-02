from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from .models import Project, Comment, Donation, Rating, Report
from .forms import ProjectForm, CommentForm, RatingForm


@login_required
def create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save(tags=form.cleaned_data.get("tags_input", []))
            messages.success(request, "Project created successfully!")
            return redirect("projects:all")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm()

    return render(request, "projects/create.html", {"form": form})


def all_projects(request):
    query = request.GET.get("q")
    if query:
        projects = Project.objects.filter(title__icontains=query)
    else:
        projects = Project.objects.all()
    return render(request, "projects/all.html", {"projects": projects})


def detail(request, title):
    project = get_object_or_404(Project, title=title)
    comments = Comment.objects.filter(project=project)
    donations = Donation.objects.filter(project=project)
    return render(
        request,
        "projects/detail.html",
        {
            "project": project,
            "rating": project.average_rating,
            "comments": comments,
            "donations": donations,
            "forms": {"comment": CommentForm, "rating": RatingForm},
            "similar_projects": project.similar_projects(),
        },
    )


@login_required
def cancel(request, title):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    project = get_object_or_404(Project, title=title)

    if request.user != project.creator:
        messages.error(request, "You are not authorized to cancel this project.")
        return redirect("projects:detail", title=title)

    if not project.cancellable:
        messages.error(request, "This project cannot be canceled.")
        return redirect("projects:detail", title=title)

    project.delete()
    messages.success(request, "Project canceled successfully.")

    return redirect("projects:all")


@login_required
def __action__(request, title, model, field_name):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    value = request.POST.get(field_name)
    project = get_object_or_404(Project, title=title)
    model.objects.create(user=request.user, project=project, **{field_name: value})
    return redirect("projects:detail", title=project.title)


def comment(request, title):
    return __action__(request, title, Comment, "content")


def donate(request, title):
    return __action__(request, title, Donation, "amount")


def report(request, title):
    return __action__(request, title, Report, "reason")


def rate(request, title):
    return __action__(request, title, Rating, "value")
