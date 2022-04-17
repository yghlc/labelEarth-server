from django.db import models

from django.contrib.auth.models import User

# Create your models here.
# A model is the single, definitive source of information about your data.

class Image(models.Model):
    image_name = models.CharField(max_length=200,unique=True)
    image_path = models.FilePathField()
    # the geojson file for this image
    image_object_path = models.FilePathField()
    image_bound_path = models.FilePathField(default=None)

    # how many user are working on the same image
    concurrent_count = models.IntegerField(default=0)

    image_valid_times = models.IntegerField(default=0)

    # center lat and lon
    image_cen_lat = models.FloatField(default=None)
    image_cen_lon = models.FloatField(default=None)

    def __str__(self):
        return self.image_name

class UserInput(models.Model):

    user_name = models.ForeignKey(User,on_delete=models.CASCADE)
    image_name = models.ForeignKey(Image,on_delete=models.CASCADE)
    # if a user input, then save to a file
    user_image_output = models.FilePathField(default=None)
    saving_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.user_name) + ' edit objects on ' + str(self.image_name)









