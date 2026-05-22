from django.urls import path
from .views import (
    login_view,
    welcome_view,
    logout_view,
    requests_without_optimization,
    requests_with_optimization,
    book_list,
    start_import,
    task_status,
    stats_view,
    authors_with_popular_books,
    books_count,
    mongo_books
    )

urlpatterns = [
    path('', welcome_view, name='welcome'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('without/', requests_without_optimization),
    path('with/', requests_with_optimization),
    path('books/', book_list),
    path("import/", start_import),
    path("task/<task_id>/", task_status),
    path("stats/", stats_view),
    path("authors_popular/", authors_with_popular_books),
    path("books_count/", books_count),
    path("mongo_books/", mongo_books)
]