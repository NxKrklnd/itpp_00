from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import TrainerRegistration, CourseInfo, CourseDetails

def home(request):
    courses = CourseInfo.objects.select_related('details').all()
    return render(request, 'lms/home.html', {'courses': courses})

def user_registration(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate required fields
        if not all([first_name, last_name, username, email, password, confirm_password]):
            messages.error(request, 'All fields are required!')
            return redirect('user_registration')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format!')
            return redirect('user_registration')

        # Validate password
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return redirect('user_registration')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('user_registration')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('user_registration')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('user_registration')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return redirect('user_registration')

    return render(request, 'lms/user_registration.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Both username and password are required!')
            return redirect('login')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'lms/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def learn_as_trainer(request):
    if hasattr(request.user, 'trainerregistration'):
        messages.error(request, 'You have already applied as a trainer!')
        return redirect('home')

    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        
        if not mobile:
            messages.error(request, 'Mobile number is required!')
            return redirect('learn_as_trainer')

        try:
            TrainerRegistration.objects.create(
                user=request.user,
                mobile=mobile
            )
            messages.success(request, 'Your trainer application has been submitted for review.')
            return redirect('home')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('learn_as_trainer')

    return render(request, 'lms/learn_as_trainer.html')

@login_required
def create_course(request):
    if not hasattr(request.user, 'trainerregistration') or \
       not request.user.trainerregistration.status:
        messages.error(request, 'You must be an approved trainer to create courses!')
        return redirect('home')

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        course_image = request.FILES.get('course_image')

        if not all([course_name, category, description, course_image]):
            messages.error(request, 'All fields are required!')
            return redirect('create_course')

        try:
            course = CourseInfo.objects.create(
                trainer=request.user,
                course_name=course_name,
                category=category
            )

            CourseDetails.objects.create(
                course=course,
                description=description,
                course_image=course_image
            )

            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', slug=course.slug)
        except Exception as e:
            messages.error(request, 'An error occurred while creating the course. Please try again.')
            return redirect('create_course')

    categories = dict(CourseInfo.CATEGORY_CHOICES)
    return render(request, 'lms/create_course.html', {'categories': categories})
