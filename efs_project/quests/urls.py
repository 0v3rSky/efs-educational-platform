from django.urls import path
from . import views

app_name = 'quests'

urlpatterns = [
    path('', views.quest_list, name='quest_list'),
    path('<int:pk>/', views.quest_detail, name='quest_detail'),
    path('<int:pk>/section/<int:section_idx>/', views.quest_section, name='quest_section'),
    path('<int:pk>/quiz/', views.quest_quiz, name='quest_quiz'),
    path('<int:pk>/quiz/step/<int:step>/', views.quest_quiz_step, name='quest_quiz_step'),
    path('api/quests/<int:topic_id>/', views.get_quests_by_topic, name='get_quests_by_topic'),
] 