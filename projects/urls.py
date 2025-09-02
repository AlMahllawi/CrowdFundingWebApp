from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.all_projects, name="all"),
    path("create/", views.create, name="create"),
    path("view/<str:title>/", views.detail, name="detail"),
    path("cancel/<str:title>/", views.cancel, name="cancel"),
    path("comment/<str:title>/", views.comment, name="comment"),
    path("donate/<str:title>/", views.donate, name="donate"),
    path("report/<str:title>/", views.report, name="report"),
    path("rate/<str:title>/", views.rate, name="rate"),
    path("report/<str:title>/", views.report, name="report"),
    path("report-comment/<int:comment_id>/", views.report, name="report"),
]
