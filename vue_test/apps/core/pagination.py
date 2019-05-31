from rest_framework.pagination import PageNumberPagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    # 前端动态传递参数控制当页显示条数
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100