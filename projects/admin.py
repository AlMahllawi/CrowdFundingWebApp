from django.contrib import admin
from .models import Project, ProjectImage, Comment, Rating, Report, Donation

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class DonationInline(admin.TabularInline):
    model = Donation
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "category", "target_amount", "current_amount", "start_date", "end_date")
    search_fields = ("title", "details", "tags")
    list_filter = ("category", "start_date", "end_date")
    inlines = [ProjectImageInline, DonationInline]

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("project", "image")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "content", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at",)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "value")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "project", "comment", "user", "is_resolved", "created_at")
    list_filter = ("report_type", "is_resolved")
    search_fields = ("reason",)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "amount", "created_at")
    list_filter = ("created_at",)