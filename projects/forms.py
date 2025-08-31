from django import forms
from .models import Project, Comment, Rating, Report

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "details", "category", "target_amount", "start_date", "end_date", "tags"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason"]