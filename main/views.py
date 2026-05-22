import time

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db.models import Count, Avg
from django.db import connection
from celery.result import AsyncResult

from .forms import LoginForm
from .models import Book, Author
from .tasks import import_books_and_notify
from .mongo_models import BookDoc


def login_view(request: HttpRequest) -> HttpResponse:
    """Renders the login page."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            age = form.cleaned_data["age"]

            response = redirect("welcome")

            response.set_cookie("name", name, max_age=60*60*24)
            request.session["age"] = age

            return response
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {'form': form})


def welcome_view(request: HttpRequest) -> HttpResponse:
    """Renders the welcome page."""
    name = request.COOKIES.get("name")
    age = request.session.get("age")

    if not name or not age:
        return redirect("login")

    response = render(request, "main/welcome.html", {
        "name": name,
        "age": age
    })

    response.set_cookie("name", name, max_age=60*60*24)

    return response


def logout_view(request: HttpRequest) -> HttpResponse:
    """Renders the logout page."""
    response = redirect("login")

    response.delete_cookie("name")
    request.session.flush()

    return response


def requests_without_optimization(request: HttpRequest) -> HttpResponse:
    """Renders the page with time about ORM requests without optimization."""
    start = time.time()

    books = Book.objects.all()

    for book in books:
        _ = book.author.name
        for r in book.reviews.all():
            _ = r.review

    end = time.time()

    return HttpResponse(f"Without optimization: {end - start:.4f}")


def requests_with_optimization(request: HttpRequest) -> HttpResponse:
    """Renders the page with time about ORM requests with optimization."""
    start = time.time()

    books = Book.objects.select_related("author").prefetch_related("reviews")

    for book in books:
        _ = book.author.name
        for r in book.reviews.all():
            _ = r.review

    end = time.time()

    return HttpResponse(f"With optimization: {end - start:.4f}")


def book_list(request: HttpRequest) -> HttpResponse:
    """Renders the book list page."""
    books = cache.get("book_list")

    if not books:
        books = list(
            Book.objects.select_related("author").prefetch_related("reviews")
        )
        cache.set("book_list", books, 60)

    return render(request, "main/books_list.html", {
        "books": books
    })


def start_import(request: HttpRequest) -> JsonResponse:
    """Renders the start page."""
    task = import_books_and_notify.delay(
        "books.csv",
        request.user.email
    )

    return JsonResponse({"task_id": task.id})


def task_status(request: HttpRequest, task_id) -> JsonResponse:
    """Renders the task status page."""
    task = AsyncResult(task_id)

    return JsonResponse({
        "task_id": task_id,
        "status": task.status,
        "result": task.result
    })

def stats_view(request):
    books = (
        Book.objects
        .select_related("author")
        .annotate(
            reviews_count=Count("reviews"),
            avg_rating=Avg("reviews__rating")
        )
        .order_by("-reviews_count", "-avg_rating")
    )

    authors = (
        Author.objects
        .annotate(avg_rating=Avg("book__reviews__rating"))
    )

    return render(request, "main/stats.html", {
        "books": books,
        "authors": authors
    })


def authors_with_popular_books(request: HttpRequest) -> JsonResponse:
    """Renders the authors with popular books page."""
    min_reviews = 10

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.name, COUNT(b.id) as books_count
            FROM main_author a
            JOIN main_book b ON b.author_id = a.id
            JOIN main_review r ON r.book_id = b.id
            GROUP BY a.id
            HAVING COUNT(r.id) > %s
        """, [min_reviews])

        rows = cursor.fetchall()

    data = [
        {
            "id": r[0],
            "name": r[1],
            "books_count": r[2],
        }
        for r in rows
    ]

    return JsonResponse({"authors": data})


def books_count(request: HttpRequest) -> JsonResponse:
    """Renders the books count page."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM main_book
        """)

        count = cursor.fetchone()[0]

    return JsonResponse({"books_count": count})


def mongo_books(request: HttpRequest) -> JsonResponse:
    """Renders the mongo books page."""
    start = time.time()
    books = BookDoc.objects()

    data = [
        {
            "title": b.title,
            "author": b.author_name,
            "rating": b.rating,
        }
        for b in books
    ]

    end = time.time()

    return JsonResponse({"books": data, "time": end - start})