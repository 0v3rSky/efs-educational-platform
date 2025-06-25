import nested_admin
from django.contrib import admin
from .models import Quest, QuestSection, QuestQuiz, QuestQuizQuestion, QuestQuizAnswer, QuestTopic

class QuestSectionInline(admin.TabularInline):
    model = QuestSection
    extra = 1

class QuestQuizAnswerInline(nested_admin.NestedTabularInline):
    model = QuestQuizAnswer
    extra = 1

class QuestQuizQuestionInline(nested_admin.NestedTabularInline):
    model = QuestQuizQuestion
    inlines = [QuestQuizAnswerInline]
    extra = 1

class QuestQuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestQuizQuestionInline]

class QuestAdmin(admin.ModelAdmin):
    inlines = [QuestSectionInline]

admin.site.register(Quest, QuestAdmin)
admin.site.register(QuestSection)
admin.site.register(QuestQuiz, QuestQuizAdmin)
admin.site.register(QuestQuizQuestion)
admin.site.register(QuestQuizAnswer)
admin.site.register(QuestTopic)
