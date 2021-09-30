import auctions
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.db.models.base import Model
from django.db.models.query_utils import refs_expression
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms import ModelForm, widgets
from django.urls.base import is_valid_path
from django.contrib.auth.decorators import login_required

from .models import *



class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startingBid', 'category', 'imageUrl']
        labels = {
            
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'startingBid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'imageUrl': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        
        fields = ['offer']
        labels = {
            'offer': '',
        }
        widgets = {
            'offer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bid'
            })
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        labels = {
            'comment':'',
        }
        widgets = { 
            'comment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave your comment here'
            })
        }

def watchCount(request):
    if request.user.is_authenticated:
        listings = request.user.watched_listings.all()
        wcount = len(listings)
    else:
        wcount = None
    return wcount

def is_watched(request,listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user in listing.watchers.all():
        listing.is_watched = True
    else:
        listing.is_watched = False
    return listing.is_watched

def index(request):
    if request.user.is_authenticated:
        wlistings = request.user.watched_listings.all()
    else:
        wlistings = None
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(flactive = True).order_by('-created_date'),
        "wcount": watchCount(request),
        "wlistings": wlistings,
    })


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


@login_required
def newListing(request):
    if request.method == "POST":
        newListingForm = ListingForm(request.POST)
        if newListingForm.is_valid():
            newListing = newListingForm.save(commit=False)
            newListing.creator = request.user
            newListing.save()
            newListingForm.save_m2m()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/newListing.html",{
                "form": newListingForm,
                "wcount": watchCount(request)
            })

    else:
        return render(request, "auctions/newListing.html",{
            "form": ListingForm(),
            "wcount": watchCount(request)
        })


def listing(request, listing_id):
    if request.user.id is None:
        return redirect('login')
    listing = Listing.objects.get(pk=listing_id)
    listing.is_watched =  is_watched(request, listing_id)
    bidcount = len(Bid.objects.filter(auction=listing))
    if bidcount > 0:
        if request.user == Bid.objects.filter(auction=listing).last().user:
            listing.yourBid = True
        else:
            listing.yourBid = False

    return render(request,"auctions/listing.html", {
        "listing" : listing,
        "comments" : listing.get_comments.all().order_by('-createdDate'),
        "commentForm" : CommentForm(),
        "BidForm": BidForm(),
        "error_msg":request.COOKIES.get('error_msg'),
        "bidcount": bidcount,
        "wcount": watchCount(request)
    })

def comment(request , listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        commentForm = CommentForm(request.POST)
        if commentForm.is_valid():
            newcomment = commentForm.save(commit=False)
            newcomment.listing = listing
            newcomment.user = request.user
            newcomment.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            return render(request, "auctions/listing.html", {
                "commentForm": commentForm
            })
    else:
        return render(request, "auctions/listing.html", {
            "commentForm": CommentForm()
        })


def bid(request, listing_id):
    listing = Listing.objects.get(pk= listing_id)
    if listing.currentBid :
        currentBid = listing.currentBid
    else:
        currentBid = listing.startingBid
    
    if request.method == "POST":
        newBidForm = BidForm(request.POST)
        if newBidForm.is_valid():
            newBid = newBidForm.cleaned_data["offer"]
            if newBid > currentBid : 
                listing.currentBid = newBid
                listing.save()
                newbid = newBidForm.save(commit=False)
                newbid.auction = listing
                newbid.user = request.user
                newbid.save()
                return HttpResponseRedirect(reverse("listing", kwargs={'listing_id':listing.id,}))
        
            else:
                response = redirect('listing',listing_id=listing_id)
                response.set_cookie('error_msg','Bid is not greater than current price',max_age=3)
                return response
                

def closeAuction(request,listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.creator:
        listing.flactive = False
        listing.buyer = Bid.objects.filter(auction=listing).last().user
        listing.save()
        return HttpResponseRedirect(reverse('listing',args=(listing.id,)))
        

def watch(request,listing_id):
    if request.user.id is None:
        return redirect('login')
    listing = Listing.objects.get(pk=listing_id)
    if request.user not in listing.watchers.all():
        listing.watchers.add(request.user)
    else:
        listing.watchers.remove(request.user) 
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def watchlist(request):
    listings = request.user.watched_listings.all()
    wlistings = request.user.watched_listings.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "wcount": watchCount(request),
        "wlistings": wlistings,
    }) 

@login_required
def category(request):
    categorys = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categorys": categorys,
        "wcount": watchCount(request),
    })

@login_required
def category_view(request,category_id):
    category = Category.objects.get(pk = category_id)
    listings = Listing.objects.filter(category=category)
    wlistings = request.user.watched_listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "wcount": watchCount(request),
        "wlistings": wlistings,
    })
        
