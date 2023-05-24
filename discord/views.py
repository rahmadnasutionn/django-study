from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
# Create your views here.

# rooms = [
#     { 'id': 1, 'name': 'Lets learn django' },
#     { 'id': 2, 'name': 'Frontend Developer' },
#     { 'id': 3, 'name': 'Backend Developer' },
# ]

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    topic = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {
        'rooms': rooms,
        'topics': topic,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST['body']
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST['topic']
        topic, created_at = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST['name'],
            description = request.POST['description'],
        )

        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST['topic']
        topic, created_at = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST['name']
        room.topic = topic
        room.description = request.POST['description']
        room.save()

        return redirect('home')

    context = {
        'form': form,
        'room': room,
        'topics': topics,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

def login_view(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'Email does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error('Email or password are wrong')
            return redirect('login')

    context = {
        'page': page
    }
    return render(request, 'base/login_register.html', context)

def register_view(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    context = {
        'page': page,
        'form': form,
    }
    return render(request, 'base/login_register.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render (request, 'base/delete.html', {'obj': message})

def profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def settings(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('profile', pk=user.id)

    context = {
        'form': form,
    }
    return render(request, 'base/settings.html', context)

def topics_view(request):
    q = request.GET.get('q') if request.GET.get('q') else ""

    topics = Topic.objects.filter(
        Q(name__icontains=q)
    )
    context = {
        'topics': topics,
    }
    return render(request, 'base/topics.html', context)