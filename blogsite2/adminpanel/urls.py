from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.dashboard_view,    name='admin_dashboard'),
    path('block/<int:user_id>/',          views.block_user_view,   name='admin_block_user'),
    path('delete-user/<int:user_id>/',    views.delete_user_view,  name='admin_delete_user'),
    path('edit-post/<int:post_id>/',      views.edit_post_view,    name='admin_edit_post'),
    path('delete-post/<int:post_id>/',    views.delete_post_view,  name='admin_delete_post'),
    path('comments/',                     views.comments_view,     name='admin_comments'),
    path('delete-comment/<int:comment_id>/', views.delete_comment_view, name='admin_delete_comment'),
]
