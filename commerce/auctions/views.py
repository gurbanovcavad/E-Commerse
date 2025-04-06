from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, WatchListing, Bid

def index(request):
    context = {"listings": Listing.objects.all()}
    return render(request, "auctions/index.html", context)


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
        return render(request, "auctions/login.html", {
            "message": "Invalid username and/or password."
        })
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
    return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        owner = request.user
        listing = Listing(title=title, description=description,
                          starting_bid=starting_bid, image_url=image_url, category=category, owner=owner)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listing.html")

def place_bid(request, id):
    if request.method == 'POST':
        try:      
            amount = int(request.POST['bid'])
            listing = Listing.objects.get(pk=id)
            user = request.user
            bid = Bid(amount=amount, bidder=user,listing=listing)
            bid.save()
            return HttpResponseRedirect(reverse("open_listing", args=[id,]))
        except:
            return HttpResponseRedirect(reverse('open_listing', args=[id,]))
def open_listing(request, id):
    listing = Listing.objects.get(pk=id)
    count = Listing.objects.get(pk=id).bids.all().count()
    context = {"listing": listing, "count": count}
    return render(request, 'auctions/listing.html', context)

@login_required
def watch_list(request):
    user = User.objects.get(pk=request.user.id)
    watch_list = user.watch_list.all()
    listings = [Listing.objects.get(pk=listing.listing_id) for listing in watch_list]
    context = {"listings": listings} 
    return render(request, "auctions/watch_list.html", context)

@login_required
def add_watching(request, id):
    try:
        listing = WatchListing(owner=User.objects.get(pk=request.user.id), listing=Listing.objects.get(pk=id))
        listing.save()
        return HttpResponseRedirect(reverse('index'))
    except:
        return HttpResponseRedirect(reverse('index'))
    
@login_required
def delete_watchlist(request, id):
    pass