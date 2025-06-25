from django.contrib import admin
from django import forms
from .models import (
    Test,
    TextQuestion,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    Choice,
    TestResult,
    UserTextAnswer,
    UserSingleChoiceAnswer,
    UserMultipleChoiceAnswer
)

# Форма для инлайна вопросов с одним выбором
class SingleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = SingleChoiceQuestion
        fields = ['test', 'text', 'order', 'points']

# Форма для инлайна вопросов с множественным выбором
class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['test', 'text', 'order', 'points']

# Инлайн для вариантов ответов для вопросов с одним выбором
class SingleChoiceInline(admin.TabularInline):
    model = Choice
    fk_name = 'question_single'
    extra = 4 # Количество пустых форм для новых вариантов
    max_num = 4 # Максимальное количество вариантов ответа
    fields = ['text', 'is_correct']

# Инлайн для вариантов ответа для вопросов с множественным выбором
class MultipleChoiceInline(admin.TabularInline):
    model = Choice
    fk_name = 'question_multiple'
    extra = 4
    max_num = 4
    fields = ['text', 'is_correct']

# Инлайн для текстовых вопросов
class TextQuestionInline(admin.StackedInline):
    model = TextQuestion
    extra = 1 # Количество пустых форм для новых вопросов
    fields = ['text', 'order', 'points', 'correct_answer']

# Админка для вопросов с одним выбором (отдельная вкладка)
@admin.register(SingleChoiceQuestion)
class SingleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'order', 'points')
    list_filter = ('test__title',)
    search_fields = ('text', 'test__title')
    form = SingleChoiceQuestionForm
    inlines = [SingleChoiceInline]

# Админка для вопросов с множественным выбором (отдельная вкладка)
@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'order', 'points')
    list_filter = ('test__title',)
    search_fields = ('text', 'test__title')
    form = MultipleChoiceQuestionForm
    inlines = [MultipleChoiceInline]

# Админка для модели Test
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'points', 'passing_score', 'time_limit')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description')
    inlines = [TextQuestionInline]
    fields = ['title', 'description', 'image', 'category', 'difficulty', 'points', 'passing_score', 'time_limit']

# Регистрация модели TestResult и ответов пользователя в админке
@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'percent', 'passed', 'completed_at')
    list_filter = ('test', 'passed')
    search_fields = ('user__username', 'test__title')
    readonly_fields = ('completed_at', 'score', 'passed')

# Админки для ответов пользователя (для просмотра, не для редактирования)
@admin.register(UserTextAnswer)
class UserTextAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'answer_text')
    search_fields = ('test_result__user__username', 'question__text')
    readonly_fields = ('test_result', 'question', 'answer_text')

@admin.register(UserSingleChoiceAnswer)
class UserSingleChoiceAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'selected_choice')
    search_fields = ('test_result__user__username', 'question__text', 'selected_choice__text')
    readonly_fields = ('test_result', 'question', 'selected_choice')

@admin.register(UserMultipleChoiceAnswer)
class UserMultipleChoiceAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question')
    search_fields = ('test_result__user__username', 'question__text')
    readonly_fields = ('test_result', 'question', 'selected_choices')
