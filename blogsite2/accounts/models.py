from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile') #Extends Django's built-in User model  #  OneToOneField → each user has exactly one profile # Already has username, email, password, first_name, last_name built in #on_delete=models.CASCADE → if User is deleted, Profile is also deleted # related_name='profile' → lets you access profile from user like user.profile
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)  #upload_to='profiles/' → saves file inside media/profiles/ folder # blank=True → form doesn't require it # null=True → database allows empty value
    contact_number = models.CharField(max_length=15, blank=True)   #Stores phone number as text (not integer — to preserve leading zeros)
    bio = models.TextField(blank=True)                             #Stores longer text for user description TextField → no length limit unlike CharField
    is_blocked = models.BooleanField(default=False)                #Tracks if admin has blocked this user default=False → new users are not blocked by default
    created_at = models.DateTimeField(auto_now_add=True)           #Automatically saves the date and time when profile is created #auto_now_add=True → set once on creation, never change

    def __str__(self):
        return f"{self.user.username}'s profile"                  #Controls what shows in Django admin panel for this object
