from django.db.models import Q, Avg
from django.views.generic import ListView
from projects.models import Project
from .forms import SearchForm


class Main(ListView):
    model = Project
    template_name = "home/index.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
            if query.startswith("category:"):
                category_value = query[len("category:") :].strip()
                category_values = [value for value, _ in Project.CATEGORY_CHOICES]
                if category_value in category_values:
                    queryset = queryset.filter(category=category_value)
                else:
                    queryset = queryset.none()
            else:
                query_words = query.split()
                title_queries = Q()
                tag_queries = Q()

                for word in query_words:
                    title_queries |= Q(title__icontains=word)
                    tag_queries |= Q(tags__name__icontains=word)

                queryset = queryset.filter(title_queries | tag_queries).distinct()

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm(self.request.GET)
        context["query"] = self.request.GET.get("query", "")
        context["top_projects"] = Project.objects.annotate(
            avg_rating=Avg("ratings__value")
        ).order_by("-avg_rating")[:5]
        context["latest_projects"] = Project.objects.order_by("-created_at")[:5]
        context["featured_projects"] = Project.objects.filter(
            is_featured=True
        ).order_by("-created_at")[:5]
        context["categories"] = Project.CATEGORY_CHOICES
        return context
