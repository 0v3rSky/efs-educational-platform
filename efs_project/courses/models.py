from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
# from tests.models import Test

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Финансовая грамотность', 'Финансовая грамотность'),
        ('Экономика', 'Экономика'),
        ('Фондовый рынок', 'Фондовый рынок'),
    ]
    DIFFICULTY_LEVELS = [
        ('Легкий', 'Легкий'),
        ('Средний', 'Средний'),
        ('Сложный', 'Сложный'), 
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='course_images/')
    difficulty = models.CharField(max_length=8, choices=DIFFICULTY_LEVELS, default='Легкий')
    enrolled_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserCourse', related_name='enrolled_courses')
    # test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name='Тест для курса')
    points = models.PositiveIntegerField(default=100, help_text='Очки, которые получает пользователь за прохождение курса')

    def __str__(self):
        return self.title

class UserCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"

class UserCourseCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}" 