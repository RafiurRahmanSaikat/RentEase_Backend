from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get(self.page_query_param) == "all":
            # For "all", we'll handle this in the view
            return None

        return super().paginate_queryset(queryset, request, view)
