from django.db.models import Q
from django.views.generic import ListView
from django.shortcuts import render
from projects.models import Project
from .forms import SearchForm


class Search(ListView):
    model = Project
    template_name = "home/index.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
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
        return context
