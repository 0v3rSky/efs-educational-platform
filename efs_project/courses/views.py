from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, CourseSection, UserCourseCompletion
from django.http import JsonResponse

from collections import defaultdict


@login_required
def course_list(request):
    categories = Course.objects.values_list('category', flat=True).distinct()
    difficulties = [d[0] for d in Course.DIFFICULTY_LEVELS]
    completed_courses = set(UserCourseCompletion.objects.filter(user=request.user).values_list('course_id', flat=True))

    categories_data = []
    for category in categories:
        difficulties_data = []
        for difficulty in difficulties:
            courses = list(Course.objects.filter(category=category, difficulty=difficulty))
            for course in courses:
                course.is_completed = course.id in completed_courses
                if course.is_completed:
                    completion = UserCourseCompletion.objects.get(user=request.user, course=course)
                    course.completion_date = completion.completed_at
            courses.sort(key=lambda c: c.is_completed)
            difficulties_data.append((difficulty, courses))
        categories_data.append((category, difficulties_data))

    return render(request, 'courses/course_list.html', {
        'categories_data': categories_data,
    })


@login_required
def get_all_courses(request, category, difficulty):
    courses = Course.objects.filter(category=category, difficulty=difficulty)
    courses_data = [{
        'id': course.id,
        'title': course.title,
        'image_url': course.image.url,
        'description': course.description
    } for course in courses]
    return JsonResponse({'courses': courses_data})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    sections = course.sections.all().order_by('order')
    is_enrolled = course.enrolled_users.filter(id=request.user.id).exists()
    
    # Проверяем, завершен ли курс
    completion = None
    is_completed = False
    if is_enrolled:
        completion = UserCourseCompletion.objects.filter(user=request.user, course=course).first()
        is_completed = completion is not None
    
    if request.method == 'POST' and not is_enrolled:
        course.enrolled_users.add(request.user)
        return redirect('course_detail', pk=pk)
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'sections': sections,
        'is_enrolled': is_enrolled,
        'is_completed': is_completed,
        'completion': completion
    })


@login_required
def course_start(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Можно добавить проверку, что пользователь записан на курс
    is_enrolled = UserCourse.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        return redirect('course_detail', pk=pk)
    # Здесь можно добавить логику показа материалов курса
    return render(request, 'courses/course_start.html', {'course': course})


@login_required
def course_section(request, course_id, section_id):
    course = get_object_or_404(Course, pk=course_id)
    sections = course.sections.all()
    section = get_object_or_404(CourseSection, pk=section_id, course=course)
    section_ids = list(sections.values_list('id', flat=True))
    current_index = section_ids.index(section.id)
    next_section_id = section_ids[current_index + 1] if current_index + 1 < len(section_ids) else None

    # Проверяем, завершен ли курс (уже было в коде)
    completion = UserCourseCompletion.objects.filter(user=request.user, course=course).first()
    is_completed = completion is not None

    # Логика обработки POST-запроса на завершение курса
    if request.method == 'POST' and 'complete_course' in request.POST and not is_completed:
        print(f"Completing course {course.title} for the first time.")
        completion = UserCourseCompletion.objects.create(user=request.user, course=course)
        is_completed = True
        # Начисляем очки при первом завершении курса
        if request.user.profile:
            request.user.profile.add_points(course.points)
            print(f"Points ({course.points}) added for completing course {course.title}.")
        else:
            print("User profile or level not found. Cannot add points.")

        # После завершения курса, можно перенаправить пользователя, например, на страницу курса или список курсов
        # return redirect('course_detail', pk=course.pk)
        # Или остаться на этой же странице, обновив контекст

    return render(request, 'courses/course_section.html', {
        'course': course,
        'sections': sections,
        'section': section,
        'next_section_id': next_section_id,
        'is_completed': is_completed,
        'completion': completion
    })


@login_required
def complete_course(request, pk):
    print(f"complete_course view called for course pk={pk}")
    course = get_object_or_404(Course, pk=pk)
    if course.enrolled_users.filter(id=request.user.id).exists():
        print(f"User {request.user.username} is enrolled in course {course.title}")
        completion, created = UserCourseCompletion.objects.get_or_create(user=request.user, course=course)
        print(f"UserCourseCompletion object retrieved or created. Created: {created}")
        if created:
            # Начисляем очки только при первом завершении курса
            print(f"First completion of course {course.title}. Points to add: {course.points}")
            request.user.profile.add_points(course.points)
            print("add_points method called.")
        else:
            print("Course already completed by user. Points not added.")
    else:
        print(f"User {request.user.username} is NOT enrolled in course {course.title}")

    return redirect('course_detail', pk=pk)