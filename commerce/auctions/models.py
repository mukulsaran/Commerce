from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=60)

    def __str__(self):
        return self.category

class Listing(models.Model):
    title = models.CharField(max_length=60)
    flactive = models.BooleanField(default=True)
    description = models.CharField(null=True , max_length=2084)
    created_date = models.DateTimeField(default=timezone.now)
    currentBid = models.FloatField(blank=True,null=True)
    startingBid = models.FloatField()
    category = models.ForeignKey(Category, blank=True, null=True ,on_delete=models.PROTECT)
    watchers = models.ManyToManyField(User,blank=True, related_name="watched_listings")
    buyer = models.ForeignKey(User, null=True, on_delete=models.PROTECT, blank= True)
    imageUrl = models.CharField(max_length=2084)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name= "all_creator_listings")

    def __str__(self):
        return f"{self.title} - {self.startingBid}"

class Bid(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.FloatField()
    date = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    comment = models.CharField(max_length=100)
    createdDate = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="get_comments")

    def get_creation_date(self):
        return self.createdDate.strftime('%B %D %Y')