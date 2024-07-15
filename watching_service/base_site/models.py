from django.db import models

# Create your models here.


def video_directory_path(instance, filename):
    return "{0}/{1}".format(instance.film_id.id, filename)


def film_directory_path(instance, filename):
    return "posters/{0}".format(filename)


class Film(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    genres = models.CharField(max_length=100)
    description = models.CharField(max_length=400)
    release_date = models.CharField(max_length=100)
    poster_img_link = models.CharField(max_length=100)
    poster_img = models.ImageField(upload_to=film_directory_path)


class Feed(models.Model):
    film_id = models.OneToOneField(Film,
                                   on_delete=models.CASCADE,
                                   primary_key=True)
    update_date = models.DateTimeField()
    update_comment = models.CharField(max_length=200, default="")


class Video(models.Model):
    film_id = models.ForeignKey(Film,
                                on_delete=models.CASCADE,
                                null=True)
    image = models.ImageField(upload_to=video_directory_path, null=True)
    video_file = models.FileField(upload_to=video_directory_path, null=True)
    video_url = models.URLField(default='')
    episode_number = models.IntegerField()
