from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newListing", views.newListing, name="newListing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),
    path("listing/<int:listing_id>/bid", views.bid, name="bid"),
    path("listing/<int:listing_id>/closeAuction", views.closeAuction, name="closeAuction"),
    path("listing/<int:listing_id>/watch", views.watch, name="watch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("catagory_listing/<int:category_id>", views.category_view, name="category_view"),
    path("is_watched/<int:listing_id>", views.is_watched, name="is_watched")
]
