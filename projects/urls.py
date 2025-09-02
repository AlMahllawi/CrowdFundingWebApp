from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.all_projects, name="all"),
    path("create/", views.create, name="create"),
    path("<str:title>/", views.detail, name="detail"),
    path("<str:title>/comment/", views.comment, name="comment"),
    path("<str:title>/donate/", views.donate, name="donate"),
    path("<str:title>/report/", views.report, name="report"),
    path("<str:title>/rate/", views.rate, name="rate"),
]
