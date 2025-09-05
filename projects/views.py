from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from .models import Project, ProjectImage, Comment, Donation, Rating, Report
from .forms import ProjectForm, ProjectImageForm, CommentForm, RatingForm, ReportForm


@login_required
def create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save(tags=form.cleaned_data.get("tags_input", []))
            messages.success(request, "Project created successfully!")
            return redirect("home:index")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm()

    return render(request, "projects/create.html", {"form": form})


def detail(request, title):
    project = get_object_or_404(Project, title=title)
    comments = Comment.objects.filter(project=project)
    donations = Donation.objects.filter(project=project)
    return render(
        request,
        "projects/detail.html",
        {
            "project": project,
            "donations": donations,
            "comments": comments,
            "user_rating": Rating.objects.filter(
                project=project, user=request.user
            ).first(),
            "forms": {
                "comment": CommentForm,
                "rating": RatingForm,
                "image": ProjectImageForm,
            },
        },
    )


@login_required
def upload_image(request, title):
    def end(message=None, level=messages.error):
        if message:
            level(request, message)
        return redirect("projects:detail", title=title)

    if request.method != "POST":
        return end()

    project = get_object_or_404(Project, title=title)

    if request.user != project.creator:
        return end("You are not authorized to upload images for this project.")

    form = ProjectImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return end("Invalid image.")

    if not form.cleaned_data.get("image"):
        return end(request, "No valid image was selected.")

    image = form.save(commit=False)
    image.project = project
    image.save()
    return end(f"Uploaded image successfully.", messages.success)


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ProjectImage, id=image_id)
    project = image.project
    if request.user != project.creator:
        messages.error(request, "You are not authorized to delete this image.")
        return redirect("projects:detail", title=project.title)

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully.")
        return redirect("projects:detail", title=project.title)

    return render(
        request,
        "projects/delete_image_confirm.html",
        {"image": image, "project": project},
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

    return redirect("home:index")


@login_required
def __action__(request, title, model, field_name, edit=False):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    value = request.POST.get(field_name)
    project = get_object_or_404(Project, title=title)
    if edit:
        instance = model.objects.filter(project=project, user=request.user).first()
        setattr(instance, field_name, value)
        instance.save()
    else:
        model.objects.create(user=request.user, project=project, **{field_name: value})

    return redirect("projects:detail", title=project.title)


def report(request, title):
    return __action__(request, title, Report, "reason")


def donate(request, title):
    return __action__(request, title, Donation, "amount")


def comment(request, title):
    return __action__(request, title, Comment, "content")


def rate(request, title):
    return __action__(request, title, Rating, "value")


def edit_rating(request, title):
    return __action__(request, title, Rating, "value", True)


@login_required
def report(request, title=None, comment_id=None):
    if title:
        obj = get_object_or_404(Project, title=title)
    elif comment_id:
        obj = get_object_or_404(Comment, id=comment_id)
    else:
        messages.error(request, "Invalid report request.")
        return redirect("home:index")

    def init():
        return render(
            request,
            "projects/report.html",
            {
                "form": ReportForm(),
                "report_project": title is not None,
                "obj": obj,
            },
        )

    if request.method != "POST":
        return init()

    form = ReportForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the errors in the form.")
        return init()

    report = form.save(commit=False)
    report.user = request.user
    if comment_id:
        report.comment = obj
    else:
        report.project = obj
    report.save()
    messages.success(request, f"Reported successfully.")
    return redirect(
        "projects:detail",
        title=obj.project.title if comment_id else obj.title,
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def feature(request, title):
    project = get_object_or_404(Project, title=title)

    if request.method == "POST":
        project.is_featured = not project.is_featured
        project.save()
        status = "featured" if project.is_featured else "unfeatured"
        messages.success(request, f"Project '{project.title}' has been {status}.")

    return redirect("projects:detail", title=project.title)
