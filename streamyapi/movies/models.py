from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    url = models.URLField()
    year = models.PositiveSmallIntegerField()
    rating = models.PositiveSmallIntegerField()
    poster = models.URLField()
    cover = models.URLField()
    genre = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(UserModel, null=True, on_delete=models.CASCADE)


class Like(models.Model):
    user = models.ForeignKey(UserModel, null=True, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        "movies.Movie", related_name="likes", on_delete=models.CASCADE
    )
