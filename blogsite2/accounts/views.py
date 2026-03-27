import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        first_name= request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email     = request.POST.get('email', '').strip()
        contact   = request.POST.get('contact', '').strip()
        password  = request.POST.get('password', '')
        cpassword = request.POST.get('cpassword', '')
        profile_pic = request.FILES.get('profile_pic')

        errors = {}
        if not username or len(username) < 3:
            errors['username'] = 'At least 3 characters'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already taken'
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = 'Enter a valid email'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'
        if contact and not re.match(r'^\d{10,15}$', contact):
            errors['contact'] = 'Enter a valid contact number'
        if len(password) < 6:
            errors['password'] = 'At least 6 characters'
        if password != cpassword:
            errors['cpassword'] = 'Passwords do not match'

        if errors:
            return render(request, 'accounts/register.html', {'errors': errors, 'data': request.POST})

        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        Profile.objects.create(user=user, contact_number=contact, profile_pic=profile_pic)
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:                            #If the user is already logged in, there’s no need to log in again → redirect them to 'home'
        return redirect('home')
    if request.method == 'POST':                                  #request.method tells you how the client sent the HTTP request, ,,,,request.method == "POST" → when a form is submitt
        username = request.POST.get('username', '').strip()       #request.POST → dictionary of submitted form data, get('username', '') → get the value of the 'username' field, default to empty string if missing, .strip() → removes spaces before and after the username
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)    #authenticate() checks: #Does a user with this username exist? model/databse compared with variable here #Does the password match? #Returns a user object if credentials are correct, otherwise None*/
        if user:                                                              # authenticate is not None
            if hasattr(user, 'profile') and user.profile.is_blocked:          #hasattr(user, 'profile') → check if user has a related profile object, ,,,user.profile.is_blocked → check if admin blocked this account
                messages.error(request, 'Your account has been blocked by admin.')
                return redirect('login')
            login(request, user)                                             #login() → logs the user in by creating a session #Now request.user will be this user for future requests
            return redirect(request.GET.get('next', 'home'))                 #Sometimes the user tried to visit a protected page before logging in #That page is passed as a next parameter in the URL (e.g., /login/?next=/dashboard/)#request.GET.get('next', 'home') → redirect to that page if it exists, otherwise redirect to 'home'
        messages.error(request, 'Invalid username or password.')     #If authenticate() returned None, the username/password was wrong
    return render(request, 'accounts/login.html')               #If request method is "GET" or credentials were invalid, Django renders the login page template

# ✅ Flow summary
# User visits login page
# If already logged in → go to home
# User submits login form (POST)
   # Get username & password
   # Authenticated
      # If blocked → show message & stay on login page
      # If valid → log in → redirect to next page or home
   # If not authenticated → show error & stay on login page
# If user just opened page (GET) → render login page




def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            messages.success(request, 'Reset instructions sent to your email (demo).')
        else:
            messages.error(request, 'No account found with that email.')
    return render(request, 'accounts/forgot_password.html')
