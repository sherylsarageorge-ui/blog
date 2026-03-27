from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')      #ForeignKey → one-to-many relationship, One user can have multiple posts,,on_delete=models.CASCADE → if the user is deleted, their posts are deleted too,,,related_name='posts' → allows access like author.posts.all()
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)      #stored in MEDIA_ROOT/posts/
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)     #Soft delete flag → don’t remove from DB, just mark deleted

    class Meta:
        ordering = ['-created_at']                      #Default ordering → newest posts first (-created_at)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')    #access comments with post.comments.all() #1 post can have many comments
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')   #Links comment to the author...onbe author many comments
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']                 #Comments are shown oldest first by default

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


# ✅ Summary:
#
# Post → stores blog posts, optional image, created/updated timestamps, soft delete
# Comment → stores comments for posts, linked to author and post, soft delete
# Uses related_name for convenient reverse lookups
# Meta.ordering controls default ordering
# __str__ improves readability in admin and shell