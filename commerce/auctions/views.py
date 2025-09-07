from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, WatchListing, Bid, Comment, Category

def index(request):
    context = {"listings": Listing.objects.all()}
    return render(request, "auctions/index.html", context)

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

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

        password = request.POST["password"]
        confirmation_p = request.POST["confirmation"]
        if password != confirmation_p:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

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

# create listing and category 
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        if request.POST["category"]: 
            try:
                category = Category(name=request.POST["category"].lower())
                category.save()
            except:
                category = Category.objects.get(name=request.POST["category"].lower())
        else:
            category = None
        owner = request.user
        listing = Listing(title=title, description=description,
                          starting_bid=starting_bid, image_url=image_url, category=category, owner=owner)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listing.html")

def view_categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'auctions/categories.html', context)

def open_category(request, id):
    category = Category.objects.get(pk=id)
    listings = category.listings.all()
    return render(request, 'auctions/open_category.html', {'listings': listings})

def place_bid(request, id):
    if request.method == 'POST':
        try:      
            amount = float(request.POST['bid'])
            print(amount)
            listing = Listing.objects.get(pk=id)
            if amount <= listing.current_price:
                raise Exception()
            else:
                listing.current_price = amount
                listing.save()
            user = request.user
            bid = Bid(amount=amount, bidder=user,listing=listing)
            bid.save()
            return HttpResponseRedirect(reverse("open_listing", args=[id,]))
        except:
            context = {"message": "Something went wrong."}
            response = render(request, 'auctions/404.html', context)
            response.status_code = 404
            return response
    return HttpResponseRedirect(reverse('index'))
   
# bids_count, comments, is_watching     
@login_required 
def open_listing(request, id):
    listing = Listing.objects.get(pk=id)
    count = Listing.objects.get(pk=id).bids.all().count()
    comments = listing.comments.all()
    try:
        is_watching = True if User.objects.get(pk=request.user.id).watchlist.get(listing=listing) else False
    except:
        is_watching = False
    context = {"listing": listing, "count": count, 'is_watching': is_watching, 'comments': comments}
    return render(request, 'auctions/listing.html', context)

@login_required
def watch_list(request):
    user = User.objects.get(pk=request.user.id)
    watch_list = user.watchlist.all()
    listings = [Listing.objects.get(pk=listing.listing_id) for listing in watch_list]
    context = {"listings": listings} 
    return render(request, "auctions/watch_list.html", context)

@login_required
def add_watching(request, id):
    try:
        listing = WatchListing(owner=User.objects.get(pk=request.user.id), listing=Listing.objects.get(pk=id))
        listing.save()
        return HttpResponseRedirect(reverse('open_listing', args=[id,]))
    except:
        context = {"message": "Something went wrong."}
        response = render(request, 'auctions/404.html', context)
        response.status_code = 404
        return response
    
# close the listing and find the winner 
@login_required    
def close_auction(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        bids = listing.bids.all()
        listing.is_active=False
        if not bids:
            listing.save()
            return HttpResponseRedirect(reverse('index'))
        max_bid = max(bids, key=lambda x: x.amount)
        listing.winner = max_bid.bidder
        listing.save()
        print(listing.is_active)
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('index'))

@login_required
def remove_watching(request, id):
    try:
        listing = WatchListing.objects.get(owner=User.objects.get(pk=request.user.id), listing=Listing.objects.get(pk=id))
        print(listing)
        listing.delete()
        return HttpResponseRedirect(reverse('open_listing', args=[id,]))
    except:
        context = {"message": "Something went wrong."}
        response = render(request, 'auctions/404.html', context)
        response.status_code = 404
        return response
    
@login_required
def add_comment(request):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(request.POST["listing"]))
        print(listing)
        content = request.POST["content"]
        print(content)
        author = request.user
        print(author)
        try:
            comment = Comment(author=author, content=content, listing=listing)
            comment.save()
            print(comment)
            return HttpResponseRedirect(reverse('open_listing', args=[listing.id]))
        except:
            context = {"message": "Something went wrong."}
            response = render(request, 'auctions/404.html', context)
            response.status_code = 404
            return response
    return HttpResponseRedirect(reverse('index'))