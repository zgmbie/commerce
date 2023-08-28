from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,Category,Listing,Comment,Bid


def index(request):
    activeListing = Listing.objects.filter(active=True)
    all = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings" : activeListing,
        "categories":all
    })

def closeAuction(request,id):
    listingData = Listing.objects.get(pk=id)
    listingData.active = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    allComments = Comment.objects.filter(listing=listingData)
    isItOnWatchlist = request.user in listingData.watchlist.all()
    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isItOnWatchlist":isItOnWatchlist,
        "allComments":allComments,
        "isOwner":isOwner,
        "update":True,
        "message":" congrats "
    })


def addBid(request ,id):
    newBid = request.POST['newBid']
    listingData = Listing.objects.get(pk=id)
    isItOnWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user , bid=int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        isOwner = request.user.username == listingData.owner.username
        return render(request, "auctions\listing.html",{
            "listing":listingData,
             "message": "bid was updated successfully",
             "update": True,
             "isItOnWatchlist":isItOnWatchlist,
             "allComments":allComments,
             "isOwner":isOwner
        })
    else:
        isOwner = request.user.username == listingData.owner.username
        return render(request, "auctions\listing.html",{
            "listing":listingData,
             "message": "bid  updated failed",
             "update": False,
             "isItOnWatchlist":isItOnWatchlist,
             "allComments":allComments,
             "isOwner":isOwner             
        })

def addComment(request,id):
    currentUser = request.user 
    listingData = Listing.objects.get(pk=id)   
    message = request.POST["newComment"]

    newComment = Comment(
        aurthor= currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing",args = (id, )))


def watchlist(request):
    currentUser = request.user
    listings = currentUser.watchlist.all()
    return render(request,"auctions\watchlist.html",{
        "listings":listings
    })


def listing(request,id):
    listingData = Listing.objects.get(pk=id)
    isItOnWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isItOnWatchlist":isItOnWatchlist,
        "allComments":allComments,
        "isOwner":isOwner
    })

def removeWatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args = (id, )))



def addWatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args = (id, )))
    



def chosenCategory(request):
    if request.method == 'POST':
        categoryFromForm = request.POST['category']
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListing = Listing.objects.filter(active=True,category=category)
        all = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings" : activeListing,
            "categories":all
        })


def createListing(request):
    if request.method == 'GET':
        all = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories":all
        })
    else:
        name = request.POST["name"]
        description = request.POST["description"]
        imageUrl = request.POST["imageUrl"]
        price = request.POST["price"]
        category = request.POST["category"]

        currentUser = request.user

        categoryData = Category.objects.get(categoryName=category)

        bid = Bid(bid=float(price) , user= currentUser)
        bid.save()

        newListing = Listing (
            name = name,
            description = description,
            imageUrl = imageUrl,
            price = bid,
            category=categoryData,
            owner = currentUser

        ) 
        newListing.save()
        return HttpResponseRedirect(reverse(index))



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
