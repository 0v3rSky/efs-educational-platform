from django.db import models
from django.conf import settings
from django.utils import timezone

class Test(models.Model):
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

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='tests/') # Сделаем изображение обязательным
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    points = models.PositiveIntegerField(default=50, help_text='Очки, которые получает пользователь за успешное прохождение теста')
    passing_score = models.PositiveIntegerField(default=70, help_text='Минимальный процент правильных ответов для прохождения теста')
    time_limit = models.PositiveIntegerField(default=30, help_text='Время на прохождение теста в минутах') # Добавляем лимит времени

    def __str__(self):
        return self.title

class TestAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('expired', 'Истекло время'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    current_question = models.IntegerField(default=1)  # Номер текущего вопроса

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.status})"

    def is_expired(self):
        if self.status != 'in_progress':
            return False
        time_elapsed = timezone.now() - self.start_time
        return time_elapsed.total_seconds() > (self.test.time_limit * 60)

    def complete(self):
        self.status = 'completed'
        self.end_time = timezone.now()
        self.save()

    def expire(self):
        self.status = 'expired'
        self.end_time = timezone.now()
        self.save()

class TextQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='text_questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')
    correct_answer = models.CharField(max_length=500)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}..."

class SingleChoiceQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='single_choice_questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}..."

class MultipleChoiceQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='multiple_choice_questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}..."

class Choice(models.Model):
    question_single = models.ForeignKey(SingleChoiceQuestion, on_delete=models.CASCADE, related_name='choices', null=True, blank=True)
    question_multiple = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, related_name='choices', null=True, blank=True)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:30]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.question_single and self.question_multiple:
            raise ValidationError('Вариант ответа не может относиться одновременно к вопросу с одним и несколькими выборами.')
        if not self.question_single and not self.question_multiple:
            raise ValidationError('Вариант ответа должен относиться к вопросу с одним или несколькими выборами.')

class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0, help_text='Набранные очки за тест')
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    @property
    def percent(self):
        total_possible_points = sum(q.points for q in self.test.text_questions.all()) + \
                                sum(q.points for q in self.test.single_choice_questions.all()) + \
                                sum(q.points for q in self.test.multiple_choice_questions.all())
        if total_possible_points == 0:
            return 0
        return round((self.score / total_possible_points) * 100)

    class Meta:
        ordering = ['completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.percent}%"

class UserTextAnswer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='text_answers')
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.test_result.user.username} - {self.question.text[:30]}..."

class UserSingleChoiceAnswer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='single_choice_answers')
    question = models.ForeignKey(SingleChoiceQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.test_result.user.username} - {self.question.text[:30]}..."

class UserMultipleChoiceAnswer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='multiple_choice_answers')
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"{self.test_result.user.username} - {self.question.text[:30]}..."
