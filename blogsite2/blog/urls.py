from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.home_view,         name='home'),
    path('post/create/',                   views.create_post_view,  name='create_post'),
    path('post/<int:post_id>/',            views.post_detail_view,  name='post_detail'),
    path('post/<int:post_id>/edit/',       views.edit_post_view,    name='edit_post'),
    path('post/<int:post_id>/delete/',     views.delete_post_view,  name='delete_post'),
    path('comment/<int:comment_id>/edit/',   views.edit_comment_view,   name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
    path('profile/',                       views.profile_view,      name='profile'),
    path('profile/edit/',                  views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/',        views.profile_view,      name='user_profile'),
]
