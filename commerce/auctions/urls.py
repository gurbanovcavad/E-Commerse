from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/listing/", views.create_listing, name='create_listing'),
    path("watchlist/", views.watch_list, name='watch_list'),
    path("add/listing/<int:id>", views.add_watching, name="add_watching"),
    path("listing/<int:id>/", views.open_listing, name="open_listing"),
    path("place/bid/<int:id>/", views.place_bid, name='place_bid'),
    path('close/auction/<int:id>/', views.close_auction, name='close_auction'),
]
