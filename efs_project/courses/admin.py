from django.contrib import admin
from .models import Course, UserCourse, CourseSection

class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty')
    search_fields = ('title',)
    list_filter = ('category', 'difficulty')
    inlines = [CourseSectionInline]

admin.site.register(UserCourse)
admin.site.register(CourseSection)