from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from django import forms
from .models import User, AuctionListing, Bid

class NewListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'category', 'url_to_picture','starting_bid']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

# def index(request):
#     return render(request, "auctions/index.html")


def index(request):
    listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# def listing(request, listing_id):
#     listing = get_object_or_404(AuctionListing, pk=listing_id)
#     bids = Bid.objects.filter(listing=listing).order_by('-timestamp')
#     return render(request, 'auctions/listing.html', {'listing': listing, 'bids': bids})


def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    bids = Bid.objects.filter(listing=listing).order_by('-timestamp')
    bid_form = BidForm()

    if request.method == 'POST':
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            new_bid = bid_form.save(commit=False)
            new_bid.bidder = request.user
            new_bid.listing = listing

            if bids.exists() and new_bid.amount <= bids.first().amount:
                messages.error(request, 'Bid amount must be higher than the most recent bid.')
            elif new_bid.amount < listing.starting_bid:
                messages.error(request, 'Bid amount must be at least as large as the starting bid.')
            else:
                new_bid.save()
                return redirect('listing', listing_id=listing_id)
        else:
            messages.error(request, 'Invalid bid amount. Please check the input.')

    return render(request, 'auctions/listing.html', {'listing': listing, 'bids': bids, 'bid_form': bid_form})



def addlisting(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():

            form.instance.seller = request.user
            form.save()
            #return HttpResponseRedirect(reverse("auctions:index"))
            return render(request, "auctions/index.html")
        else:
            return render(request, "auctions/addlisting.html", {
                "form": form
            })
    else:
        return render(request, "auctions/addlisting.html", {
            "form": NewListingForm()
        })