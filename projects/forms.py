from django import forms
from .models import Project, ProjectImage, Comment, Rating, Report


class ProjectForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Enter tags separated by spaces.",
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "details",
            "category",
            "target_amount",
            "start_date",
            "end_date",
            "tags_input",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control"}),
        }

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get("tags_input", "")
        tags = [tag.strip() for tag in tags_input.split() if tag.strip()]
        for tag in tags:
            if len(tag) > 50:
                raise forms.ValidationError(
                    f'Tag "{tag}" is too long (max 50 characters).'
                )
        return tags


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ["image"]


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
        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Please explain why you are reporting this content.",
                }
            ),
        }
