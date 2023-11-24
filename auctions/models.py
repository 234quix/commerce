from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):
        return f"{self.username}"


# Create your models here.
class AuctionListing(models.Model):
    OPTION_CHOICES = (
        ('fashion', 'Fashion'),
        ('toys', 'Toys'),
        ('home', 'Home'),
        ('electronics', 'Electronics')
    )

    category = models.CharField(
        max_length=20,
        choices=OPTION_CHOICES,
        default='home'  # You can set a default value if needed
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    url_to_picture = models.URLField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.id}: {self.title} (${self.starting_bid})"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} : {self.user} bid {self.offer} on {self.item}"


class Comment(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date = models.DateTimeField()

    def __str__(self):
        return f"Comment by {self.user} on {self.item}"
