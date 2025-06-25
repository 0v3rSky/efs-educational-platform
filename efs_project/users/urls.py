from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.profile_view, name='edit_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('achievements/', views.achievements_view, name='achievements'),
]
