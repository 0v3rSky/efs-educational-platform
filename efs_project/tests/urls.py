from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('<int:test_id>/', views.test_detail, name='test_detail'),
    path('<int:test_id>/start/', views.test_start, name='start_test'),
    path('attempt/<int:attempt_id>/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/submit/', views.submit_test, name='submit_test'),
    path('result/<int:result_id>/', views.test_result, name='test_result'),
] 