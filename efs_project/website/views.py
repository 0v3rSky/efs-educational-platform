from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Course, CourseProgress
from tests.models import Test, TestResult
from django.db.models import Count

def index(request):
    """Главная страница"""
    # Получаем последние курсы
    latest_courses = Course.objects.all().order_by('-created_at')[:6]
    
    # Получаем популярные курсы (по количеству записавшихся пользователей)
    popular_courses = Course.objects.annotate(
        enrolled_count=Count('enrolled_users')
    ).order_by('-enrolled_count')[:6]
    
    # Получаем курсы по категориям
    categories = Course.objects.values_list('category', flat=True).distinct()
    courses_by_category = {}
    for category in categories:
        courses_by_category[category] = Course.objects.filter(category=category)[:4]
    
    # Получаем статистику для авторизованного пользователя
    user_stats = None
    if request.user.is_authenticated:
        # Статистика по курсам
        enrolled_courses = Course.objects.filter(enrolled_users=request.user)
        completed_courses = CourseProgress.objects.filter(
            user=request.user,
            is_completed=True
        ).count()
        
        # Статистика по тестам
        total_tests = Test.objects.count()
        completed_tests = TestResult.objects.filter(
            user=request.user,
            passed=True
        ).count()
        
        # Получаем последние пройденные тесты
        recent_test_results = TestResult.objects.filter(
            user=request.user,
            passed=True
        ).select_related('test').order_by('-completed_at')[:5]
        
        user_stats = {
            'enrolled_courses': enrolled_courses.count(),
            'completed_courses': completed_courses,
            'total_tests': total_tests,
            'completed_tests': completed_tests,
            'recent_test_results': recent_test_results,
        }
    
    context = {
        'latest_courses': latest_courses,
        'popular_courses': popular_courses,
        'courses_by_category': courses_by_category,
        'user_stats': user_stats,
    }
    return render(request, 'website/index.html', context) 