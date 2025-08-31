from django.db import models
from django.conf import settings


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("education", "Education"),
        ("health", "Health"),
        ("technology", "Technology"),
        ("environment", "Environment"),
        ("other", "Other"),
    ]

    creator = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    details = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.title

    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 2)
        return 0

    def can_be_cancelled(self):
        return self.current_amount < (0.25 * self.target_amount)


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="project_images/")

    def str(self):
        return f"Image for {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Comment by {self.user} on {self.project}"


class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    def str(self):
        return f"Rating {self.value} for {self.project.title}"


class Report(models.Model):
    REPORT_TYPE = [
        ("project", "Project"),
        ("comment", "Comment"),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def str(self):
        return f"Report by {self.user.username} - {self.report_type}"


class Donation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="donations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.user.username} donated {self.amount} to {self.project.title}"