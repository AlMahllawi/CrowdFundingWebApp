from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.all_projects, name="all"),
    path("create/", views.create, name="create"),
    path("view/<str:title>/", views.detail, name="detail"),
    path("upload-image/<str:title>/", views.upload_image, name="upload-image"),
    path("delete-image/<int:image_id>/", views.delete_image, name="delete-image"),
    path("cancel/<str:title>/", views.cancel, name="cancel"),
    path("comment/<str:title>/", views.comment, name="comment"),
    path("donate/<str:title>/", views.donate, name="donate"),
    path("report/<str:title>/", views.report, name="report"),
    path("rate/<str:title>/", views.rate, name="rate"),
    path("report/<str:title>/", views.report, name="report"),
    path("report-comment/<int:comment_id>/", views.report, name="report"),
]
