from django.urls import path

from .views import home, room, create_room, update_room, delete_room, login_view, logout_view, register_view, delete_message, profile, settings, topics_view
# Create your urls here.

urlpatterns = [
    path('', home, name='home'),
    path('room/<str:pk>/', room, name='room'),

    path('create-room/', create_room, name='create-room'),
    path('update-room/<str:pk>/', update_room, name='update-room'),
    path('delete-room/<str:pk>/', delete_room, name='delete-room'),

    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('delete-message/<str:pk>/', delete_message, name='delete-message'),
    path('profile/<str:pk>/', profile, name='profile'),
    path('settings', settings, name='settings'),
    path('topics', topics_view, name='topics')
]
