from django.contrib import admin

# Register your models here.

from .models import Course, Test, Question, Answer


# pages of courses and tests
admin.site.register(Course)
admin.site.register(Test)

# part for testing users, logic of tests
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]