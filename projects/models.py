from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("education", "Education"),
        ("health", "Health"),
        ("technology", "Technology"),
        ("environment", "Environment"),
        ("other", "Other"),
    ]

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255, primary_key=True)
    details = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

    @property
    def current_amount(self):
        return self.donations.aggregate(models.Sum("amount"))["amount__sum"] or 0

    @property
    def average_rating(self):
        return self.ratings.aggregate(models.Avg("value"))["value__avg"] or 0

    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 2)
        return 0

    @property
    def cancellable(self):
        return self.current_amount < (0.25 * float(self.target_amount))

    def similar_projects(self, limit=4):
        return (
            Project.objects.filter(tags__in=self.tags.all())
            .exclude(title=self.title)
            .distinct()[:limit]
        )

    def save(self, *args, **kwargs):
        tags = kwargs.pop("tags", None)
        super().save(*args, **kwargs)
        if tags:
            self.tags.clear()
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                self.tags.add(tag)


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="project_images/")

    def __str__(self):
        return f"Image for {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.project}"


class Rating(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f"Rating {self.value} for {self.project.title} by {self.user.username}"


class Report(models.Model):
    REPORT_TYPE = [
        ("project", "Project"),
        ("comment", "Comment"),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} - {self.report_type}"


class Donation(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="donations"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} donated {self.amount} to {self.project.title}"
