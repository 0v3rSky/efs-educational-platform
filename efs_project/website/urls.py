from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:pk>/', views.test_detail, name='test_detail'),
    path('tests/<int:pk>/take/', views.take_test, name='take_test'),
]
