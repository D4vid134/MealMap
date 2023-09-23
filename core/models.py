from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Restaurant(models.Model):
    name = models.CharField(unique=True, max_length=255)
    address = models.TextField()
    place_id = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class UserRestaurantData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    times_eaten = models.PositiveIntegerField(default=0)
    user_rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    user_comment = models.TextField(blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    favorite_dish = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'restaurant']
    
    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name}"
