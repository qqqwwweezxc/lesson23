import csv
from celery import shared_task
from .models import Book, Author
from django.core.mail import send_mail


@shared_task(bind=True)
def import_books_from_csv(self, file_path):
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            author, _ = Author.objects.get_or_create(
                name=row["name"]
            )

            Book.objects.create(
                title=row["title"],
                author=author
            )

    return "Import completed"


@shared_task
def send_completion_email(email):
    send_mail(
        subject="Import completed",
        message="Your CSV import is finished successfully.",
        from_email="admin@example.com",
        recipient_list=[email],
        fail_silently=True
    )

@shared_task
def import_books_and_notify(file_path, email):
    import_books_from_csv(file_path)
    send_completion_email(email)
    return "Done"