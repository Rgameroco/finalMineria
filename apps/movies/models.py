from django.db import models

class Movie(models.Model):
    """Model definition for Movie."""

    title = models.CharField(max_length = 255)
    generes = models.TextField()

    class Meta:
        """Meta definition for Movie."""

        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        """Unicode representation of Movie."""
        return self.title


class Tag(models.Model):
    """Model definition for Tag."""

    user = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE)
    tag = models.CharField(max_length = 255)
    timestamp = models.IntegerField()

    class Meta:
        """Meta definition for Tag."""

        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        """Unicode representation of Tag."""
        return self.tag


class Link(models.Model):
    """Model definition for Link."""

    movie = models.ForeignKey(Movie, on_delete = models.CASCADE)
    imdb_id = models.CharField(max_length = 20, null = True)
    tmdb_id = models.IntegerField(null = True)

    class Meta:
        """Meta definition for Link."""

        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __str__(self):
        """Unicode representation of Link."""
        return self.movie.id


class Rating(models.Model):
    """Model definition for Rating."""

    user = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE)
    rating = models.FloatField()
    timestamp = models.IntegerField()

    class Meta:
        """Meta definition for Rating."""

        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        """Unicode representation of Rating."""
        return str(self.rating)


class Matriz(models.Model):
    movie1 = models.IntegerField()
    movie2 = models.IntegerField()
    desviacion = models.FloatField()