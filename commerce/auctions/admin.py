from django.contrib import admin

from .models import Comment, Listing, Bid

# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'content']
    
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'category', 
                    'winner', 'starting_bid', 'current_price']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['amount', 'bidder', 'amount']
