from django.db import models
from django.contrib.auth.models import User

class QuestTopic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name

class Quest(models.Model):
    topic = models.ForeignKey(QuestTopic, on_delete=models.CASCADE, related_name='quests', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='quest_images/', blank=True, null=True)
    points = models.PositiveIntegerField(default=75, help_text='Очки, которые получает пользователь за прохождение квеста')

    def __str__(self):
        return self.title

class QuestSection(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quest.title} — {self.title}"

class QuestQuiz(models.Model):
    quest = models.OneToOneField(Quest, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255, default='Мини-тест')

    def __str__(self):
        return f"Тест для {self.quest.title}"

class QuestQuizQuestion(models.Model):
    quiz = models.ForeignKey(QuestQuiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=512)

    def __str__(self):
        return self.text

class QuestQuizAnswer(models.Model):
    question = models.ForeignKey(QuestQuizQuestion, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
