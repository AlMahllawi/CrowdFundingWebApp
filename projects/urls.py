from django.urls import path
from . import views

app_name="projects"

urlpatterns = [
    path("projects", views.project_list, name="project_list"),
    path("<int:project_id>/", views.project_detail, name="project_detail"), 
    path("<int:project_id>/comment/",views.add_comment,name="add_comment"),
    path("<int:project_id>/donate/",views.donate_to_project, name="donate_to_project"),
    path("<int:project_id>/report/",views.report_project,name="report_project"), 
    path("<int:project_id>/rate/",views.rate_project,name="rate_project"),

]
   

