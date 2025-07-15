from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class StandardResultsSetPagination(JsonApiPageNumberPagination):
    page_size = 10
    max_page_size = 100
