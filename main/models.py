from django.db import models
from django.core.cache import cache


class Author(models.Model):
    """Model definition for Author."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    """Model definition for Book."""
    title = models.CharField(max_length=100, db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete("book_list")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete("book_list")


class Review(models.Model):
    """Model definition for Review."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    rating = models.PositiveIntegerField(db_index=True)

    def __str__(self):
        return f'Review for {self.book.title}'