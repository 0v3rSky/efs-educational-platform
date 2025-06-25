from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('api/courses/<str:category>/<str:difficulty>/', views.get_all_courses, name='get_all_courses'),
    path('<int:pk>/start/', views.course_start, name='course_start'),
    path('<int:course_id>/start/<int:section_id>/', views.course_section, name='course_section'),
]