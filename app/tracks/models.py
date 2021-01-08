from django.db import models

# Create your models here.
class Track(models.Model):
    """ An example of a database table initiliazed as a model class
    """
    # id field added automatically
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

