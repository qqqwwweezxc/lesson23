from mongoengine import connect
from mongoengine import Document, StringField, IntField


connect(
    db="lesson23",
    host="mongodb://localhost:27017/lesson23"
)


class BookDoc(Document):
    """Mongo model for books"""
    title = StringField()
    author_name = StringField()
    rating = IntField()
