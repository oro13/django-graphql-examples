from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Track(models.Model):
    """ An example of a database table initiliazed as a model class
    """
    # id field added automatically
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(get_user_model(), null=True, on_delete =
                                  models.CASCADE)  
    # posted_by associates tracks with the User table, 
    # null=True is for Django version 2, for migrations to be compatible
    # CASCADE delete means when a user is deleted, anything referenced by its
    # foreign key will be deleted as well. in the case, any associated tracks.

class Like(models.Model):
    user = models.ForeignKey(get_user_model(), null=True,
                             on_delete=models.CASCADE)
    track = models.ForeignKey('tracks.Track', related_name='likes',
                              on_delete=models.CASCADE)
