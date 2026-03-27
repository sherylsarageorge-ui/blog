from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Profile
from .models import Post, Comment


@login_required                                  #@login_required checks — are you logged in? No
                                                  #Django redirects you to the login URL (in settings)
def home_view(request):
    query = request.GET.get('q', '')               #dictionary of URL query parameters # 'q' is from html(from where request came via url) used to access a specific value.#Empty string if no search
    posts = Post.objects.filter(is_deleted=False)   #Only fetch non-deleted posts
    if query:                                      # search value is there
        posts = posts.filter(
            Q(title__icontains=query) |           # model values compared with variables here
            Q(content__icontains=query) |           #icontains → case-insensitive search
            Q(author__username__icontains=query)     #author__username → double underscore traverses the relationship to User model
        )
    # no search
    paginator = Paginator(posts, 6)    # 6 posts per page ...paginator stores full posts
    page = paginator.get_page(request.GET.get('page'))  #current page data #get_page() safely handles invalid page numbers and paginator gives data of pageno. # page is name used in html #request.GET.get('page') gives the page no.
    return render(request, 'blog/home.html', {'page': page, 'query': query})    #html :variable used here,,,render is response to Get send by browser when views is called...context will be needed when variables are there before checking POST and also render is there


# Flow Summary (simplified)
#
# Read the search query from URL.
# Fetch all non-deleted posts.
# If query exists → filter posts by title, content, or author.
# Paginate posts (6 per page).
# Render template with current page posts and search query.

@login_required
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_deleted=False)      #Fetches post by ID #If not found or deleted → automatically returns 404 page #Safer than Post.objects.get() which raises an exception
    comments = post.comments.filter(is_deleted=False)
    if request.method == 'POST':                                      # gets from post_detail.html if comment is posted
        content = request.POST.get('content', '').strip()            ##Gets the comment text from the form (<textarea name="content">),,.strip() → removes extra spaces,,,Default '' avoids errors if field is missing
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)   #Only create comment if it's not empty,,,Saves a new Comment object in database:,,,,linked to the current post,,,,author is request.user,,,,content is the submitted text
        return redirect('post_detail', post_id=post_id)                        #After submitting a comment, redirect back to the same page,,,Prevents duplicate submissions if user refreshes
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})  #if the user dont post, it will show existing posts and comments


# ✅ Full Flow (Simple)
# 🟢 When user opens the page (GET):
# Fetch post
# Fetch comments
# Render post_detail.html
# 🔵 When user submits a comment (POST):
# Get form data (content)
# Validate (not empty)
# Create comment
# Redirect back to same page                          This is called POST-Redirect-GET pattern
# Page reloads with new comment

@login_required
def create_post_view(request):
    if request.method == 'POST':                              # if post is created
        title   = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        image   = request.FILES.get('image')
        errors  = {}
        if not title:   errors['title']   = 'Title is required'
        if not content: errors['content'] = 'Content is required'
        if errors:
            return render(request, 'blog/create_post.html', {'errors': errors, 'data': request.POST})  #Passes data=request.POST → so the user’s previously typed input is preserved
        Post.objects.create(author=request.user, title=title, content=content, image=image)  # currently logged-in user becomes the author
        messages.success(request, 'Post published!')
        return redirect('home')                                        # after successful post creation it is redirected to home..not going to next render
    return render(request, 'blog/create_post.html')       #no prefill data required and also redirecting after creating..so no context

# Summary Flow
# Check if form submitted (POST) → validate input.
# If invalid → show form again with errors and pre-filled data.
# If valid → create post in database, show success message, redirect to home.
# If GET request → show empty form.


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user, is_deleted=False)
    if request.method == 'POST':                             # request comes from client HTML page
        post.title   = request.POST.get('title', post.title).strip()               #name and value in html
        post.content = request.POST.get('content', post.content).strip()
        if request.FILES.get('image'):                                            #image :name in html
            post.image = request.FILES['image']
        post.save()
        messages.success(request, 'Post updated!')
        return redirect('post_detail', post_id=post.id)
    return render(request, 'blog/edit_post.html', {'post': post})    #You need to pre-fill the form with existing post data..so context needed

# 🔹 Flow Explanation
# Fetch the Post
# Only the author can edit
# Only posts not marked deleted
# 404 if not found
# POST Request (Form submitted)
# Update title and content (keep old values if empty)
# Update image if a new one was uploaded
# Save changes
# Add success message
# Redirect to the post’s detail page
# GET Request (Form not submitted yet)
# Render the form pre-filled with the post’s current data


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.is_deleted = True
    post.save()
    messages.success(request, 'Post deleted.')
    return redirect('home')

# 🔹 Flow Explanation
# Fetch Post
# Only the author can delete the post
# If post not found → 404
# Soft Delete
# Set is_deleted = True
# Save to database
# Success Message
# Add a flash message so user knows the action succeeded
# Redirect
# Send user back to home page


@login_required
def edit_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()      #comment  which is added
        if content:
            comment.content = content
            comment.save()
        return redirect('post_detail', post_id=comment.post.id)
    return render(request, 'blog/edit_comment.html', {'comment': comment})

# 🔹 Flow Explanation
# Fetch Comment
# Only the author can edit
# 404 if not found
# POST Request (Form submitted)
# Extract content from form
# Update and save comment if content is not empty
# Redirect to the related post’s detail page
# GET Request (Form not submitted yet)
# Show the edit form with the current comment


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post_id = comment.post.id
    comment.is_deleted = True
    comment.save()
    return redirect('post_detail', post_id=post_id)

# 🔹 Flow Explanation
# Fetch Comment
# Only the comment’s author can delete it
# If comment not found → 404
# Soft Delete
# Set is_deleted = True
# Save to database
# Redirect
# Send the user back to the post’s detail page


@login_required
def profile_view(request, username=None):             #username=None → optional parameter. If no username is provided in the URL, it defaults to None.
    target = get_object_or_404(User, username=username) if username else request.user   #Goal: figure out whose profile to show.,if username: → if the URL provided a username:,,,get_object_or_404(User, username=username):Looks up a User object in the database with that username. If no user is found, Django raises a 404 Not Found error.,,,,else: request.user → if no username was provided, show the currently logged-in user’s profile.,,,target now contains the user whose profile will be displayed.
    profile, _ = Profile.objects.get_or_create(user=target)             #Tries to get the Profile associated with target.,,If it doesn’t exist, creates a new Profile automatically.
    posts = Post.objects.filter(author=target, is_deleted=False)       #Fetch all posts authored by this user that are not deleted.
    return render(request, 'blog/profile.html', {
        'profile_user': target, 'profile': profile, 'posts': posts            #Render the template blog/profile.html with context data:profile_user': target → the user whose profile is being displayed,, profile → the user’s Profile object,, posts → the user’s posts
    })
#
# Control Flow Summary
# Determine the target user (username from URL or logged-in user).
# Make sure a Profile object exists for that user.
# Fetch all their non-deleted posts.
# Render the profile template with the user, profile, and posts.


@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)             #Fetch the Profile object for the currently logged-in user (request.user),,,If the profile doesn’t exist yet, create a new one automatically..
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name  = request.POST.get('last_name', '').strip()
        request.user.email      = request.POST.get('email', '').strip()
        request.user.save()
        profile.contact_number = request.POST.get('contact', '').strip()
        profile.bio            = request.POST.get('bio', '').strip()
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return render(request, 'blog/edit_profile.html', {'profile': profile})  #If the request is not POST (i.e., GET), it will skip this block and render the form instead.

# 🔹 Summary Flow
# User requests edit_profile_view
# │
# ├── Fetch (or create) Profile for logged-in user
# │
# ├── Check request method
# │     if POST:
# │         Update User fields (first_name, last_name, email)
# │         Update Profile fields (contact, bio, profile_pic)
# │         Save User and Profile
# │         Add success message
# │         Redirect to profile page
# │
# └── Else (GET):
#       Render edit profile form pre-filled with existing profile data
