from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName


class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User,on_delete = models.CASCADE ,blank=True , null=True,related_name="userBid") 

    def __str__(self):
        return self.bid

class Listing(models.Model):
    name = models.CharField(max_length=35)
    description = models.CharField(max_length=256)
    imageUrl = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid,on_delete=models.CASCADE , blank=True,null=True,related_name="bidPrice")
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete = models.CASCADE ,blank=True , null=True,related_name="user")
    category = models.ForeignKey(Category,on_delete= models.CASCADE ,blank=True , null=True,related_name="category")
    watchlist = models.ManyToManyField(User,blank=True,null=True,related_name="watchlist")


    def __str__(self):
        return self.name

class Comment(models.Model):
    aurthor = models.ForeignKey(User,on_delete = models.CASCADE ,blank=True , null=True,related_name="userComment") 
    listing = models.ForeignKey(Listing,on_delete = models.CASCADE ,blank=True , null=True,related_name="listingComment")
    message = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.aurthor} comment on {self.listing}"
