from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Test, TestResult, UserTextAnswer, UserSingleChoiceAnswer, UserMultipleChoiceAnswer, TestAttempt
from users.models import UserLevel
from collections import defaultdict
from django.http import JsonResponse

@login_required
def test_list(request):
    """Список всех доступных тестов"""
    # Получаем все тесты, сгруппированные по категориям и сложности
    tests = Test.objects.all().order_by('category', 'difficulty', 'title')
    
    # Фильтруем тесты по нужным категориям
    allowed_categories = ['Финансовая грамотность', 'Экономика', 'Фондовый рынок']
    tests = tests.filter(category__in=allowed_categories)
    
    # Получаем результаты пользователя
    user_results = {}
    if request.user.is_authenticated:
        # Получаем только успешно пройденные тесты
        results = TestResult.objects.filter(user=request.user, passed=True)
        for result in results:
            user_results[result.test_id] = result.id
    
    # Группируем тесты по категориям и сложности
    categories_data = defaultdict(lambda: defaultdict(list))
    for test in tests:
        # Проверяем, пройден ли тест успешно
        is_completed = test.id in user_results
        # Добавляем флаг завершения к тесту
        test.is_completed = is_completed
        categories_data[test.category][test.difficulty].append(test)

    # Преобразуем defaultdict в обычный dict/list для шаблона
    # Сортируем категории и сложности для предсказуемого отображения
    sorted_categories_data = sorted(categories_data.items())
    formatted_categories_data = []
    for category, difficulties_data in sorted_categories_data:
        sorted_difficulties_data = sorted(difficulties_data.items())
        # Для каждой сложности сортируем тесты: сначала незавершенные, потом завершенные
        for difficulty, tests_list in sorted_difficulties_data:
            tests_list.sort(key=lambda x: (x.is_completed, x.title))
        formatted_categories_data.append((category, sorted_difficulties_data))

    print("Formatted Categories Data:")
    print(formatted_categories_data)

    # Дополнительный вывод содержимого списков тестов
    for category, difficulties_data in formatted_categories_data:
        print(f"Category: {category}")
        for difficulty, tests_list in difficulties_data:
            print(f"  Difficulty: {difficulty}")
            print(f"    Tests: {tests_list}")

    context = {
        'categories_data': formatted_categories_data,
        'user_results': user_results,
    }
    return render(request, 'tests/test_list.html', context)

@login_required
def test_detail(request, test_id):
    """Страница отдельного теста с вопросами"""
    test = get_object_or_404(Test, id=test_id)
    
    # Проверяем, не проходил ли пользователь тест недавно
    # recent_result = TestResult.objects.filter(
    #     user=request.user,
    #     test=test,
    #     completed_at__gte=timezone.now() - timezone.timedelta(hours=24)
    # ).first()
    
    # if recent_result:
    #     messages.warning(request, 'Вы уже проходили этот тест сегодня. Попробуйте завтра.')
    #     return redirect('tests:test_list')
    
    # Собираем все вопросы в правильном порядке
    questions = []
    questions.extend(test.text_questions.all())
    questions.extend(test.single_choice_questions.all())
    questions.extend(test.multiple_choice_questions.all())
    questions.sort(key=lambda x: x.order)
    
    context = {
        'test': test,
        'questions': questions,
    }
    return render(request, 'tests/test_detail.html', context)

@login_required
def take_test(request, attempt_id):
    """Страница прохождения теста"""
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    # Проверяем, не истекло ли время
    if attempt.is_expired():
        attempt.expire()
        messages.error(request, 'Время на прохождение теста истекло.')
        return redirect('tests:test_list')
    
    # Проверяем, не завершен ли уже тест
    if attempt.status != 'in_progress':
        messages.warning(request, 'Этот тест уже завершен.')
        return redirect('tests:test_list')
    
    # Собираем все вопросы в правильном порядке
    questions = []
    questions.extend(attempt.test.text_questions.all())
    questions.extend(attempt.test.single_choice_questions.all())
    questions.extend(attempt.test.multiple_choice_questions.all())
    questions.sort(key=lambda x: x.order)
    
    # Вычисляем оставшееся время
    time_elapsed = timezone.now() - attempt.start_time
    remaining_seconds = (attempt.test.time_limit * 60) - time_elapsed.total_seconds()
    remaining_minutes = int(remaining_seconds // 60)
    remaining_seconds = int(remaining_seconds % 60)
    
    context = {
        'attempt': attempt,
        'test': attempt.test,
        'questions': questions,
        'total_questions': len(questions),
        'remaining_time': {
            'minutes': remaining_minutes,
            'seconds': remaining_seconds
        }
    }
    
    return render(request, 'tests/take_test.html', context)

@login_required
def submit_test(request, attempt_id):
    """Обработка отправки теста и подсчет результатов"""
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if attempt.status != 'in_progress':
        messages.warning(request, 'Этот тест уже завершен.')
        return redirect('tests:test_list')
    
    if attempt.is_expired():
        attempt.expire()
        messages.error(request, 'Время на прохождение теста истекло.')
        return redirect('tests:test_list')
    
    if request.method != 'POST':
        return redirect('tests:take_test', attempt_id=attempt.id)
    
    test = attempt.test
    score = 0
    total_points = 0
    
    # Создаем запись о результате теста
    test_result = TestResult.objects.create(
        user=request.user,
        test=test,
        score=0,
        passed=False
    )
    
    # Обрабатываем текстовые вопросы
    for question in test.text_questions.all():
        answer_text = request.POST.get(f'text_{question.id}', '').strip()
        UserTextAnswer.objects.create(
            test_result=test_result,
            question=question,
            answer_text=answer_text
        )
        total_points += question.points
        if answer_text.lower() == question.correct_answer.lower():
            score += question.points
    
    # Обрабатываем вопросы с одним правильным ответом
    for question in test.single_choice_questions.all():
        choice_id = request.POST.get(f'single_{question.id}')
        if choice_id:
            try:
                choice = question.choices.get(id=choice_id)
                UserSingleChoiceAnswer.objects.create(
                    test_result=test_result,
                    question=question,
                    selected_choice=choice
                )
                total_points += question.points
                if choice.is_correct:
                    score += question.points
            except Choice.DoesNotExist:
                pass
    
    # Обрабатываем вопросы с множественным выбором
    for question in test.multiple_choice_questions.all():
        choice_ids = request.POST.getlist(f'multiple_{question.id}')
        correct_choices = set(question.choices.filter(is_correct=True))
        selected_choices = set(question.choices.filter(id__in=choice_ids))
        
        answer = UserMultipleChoiceAnswer.objects.create(
            test_result=test_result,
            question=question
        )
        answer.selected_choices.set(selected_choices)
        
        total_points += question.points
        if correct_choices == selected_choices:
            score += question.points
    
    # Обновляем результат теста
    test_result.score = score
    if total_points > 0:
        test_result.passed = (score / total_points * 100) >= test.passing_score
    else:
        test_result.passed = False
    
    test_result.save()
    
    # Завершаем попытку
    attempt.complete()
    
    # Если тест пройден успешно, начисляем очки
    if test_result.passed:
        user_profile = request.user.profile
        user_level, created = UserLevel.objects.get_or_create(profile=user_profile)
        user_level.add_points(test.points)
        messages.success(request, f'Тест пройден! Вы набрали {score} очков и получили {test.points} к своему уровню!')
    else:
        messages.warning(request, f'Тест не пройден. Вы набрали {score} очков.')
    
    return redirect('tests:test_result', result_id=test_result.id)

@login_required
def test_result(request, result_id):
    """Страница с результатами теста"""
    result = get_object_or_404(TestResult, id=result_id, user=request.user)
    
    # Собираем все ответы пользователя
    text_answers = result.text_answers.all()
    single_choice_answers = result.single_choice_answers.all()
    multiple_choice_answers = result.multiple_choice_answers.all()
    
    context = {
        'result': result,
        'text_answers': text_answers,
        'single_choice_answers': single_choice_answers,
        'multiple_choice_answers': multiple_choice_answers,
    }
    return render(request, 'tests/test_result.html', context)

@login_required
def test_start(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    # Проверяем, не начал ли пользователь уже этот тест
    active_test = TestAttempt.objects.filter(
        user=request.user,
        test=test,
        status='in_progress'
    ).first()
    
    if active_test:
        # Если тест уже начат, перенаправляем на страницу прохождения
        return redirect('tests:take_test', attempt_id=active_test.id)
    
    # Проверяем, не проходил ли пользователь тест успешно
    successful_attempt = TestResult.objects.filter(
        user=request.user,
        test=test,
        passed=True
    ).first()
    
    if successful_attempt:
        # Если тест уже пройден успешно, показываем результаты
        messages.info(request, 'Вы уже успешно прошли этот тест. Вот ваши результаты:')
        return redirect('tests:test_result', result_id=successful_attempt.id)
    
    if request.method == 'POST':
        # Создаем новую попытку прохождения теста
        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            start_time=timezone.now(),
            status='in_progress'
        )
        return redirect('tests:take_test', attempt_id=attempt.id)
    
    return render(request, 'tests/test_start.html', {
        'test': test
    })

@login_required
def save_progress(request, attempt_id):
    """Сохранение прогресса прохождения теста"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if attempt.status != 'in_progress':
        return JsonResponse({'error': 'Test is not in progress'}, status=400)
    
    if attempt.is_expired():
        attempt.expire()
        return JsonResponse({'error': 'Time expired'}, status=400)
    
    # Сохраняем ответы
    for key, value in request.POST.items():
        if key.startswith('text_'):
            question_id = int(key.split('_')[1])
            question = get_object_or_404(TextQuestion, id=question_id, test=attempt.test)
            UserTextAnswer.objects.update_or_create(
                test_result=attempt.test_result,
                question=question,
                defaults={'answer_text': value}
            )
        elif key.startswith('single_'):
            question_id = int(key.split('_')[1])
            question = get_object_or_404(SingleChoiceQuestion, id=question_id, test=attempt.test)
            choice = get_object_or_404(Choice, id=value, question=question)
            UserSingleChoiceAnswer.objects.update_or_create(
                test_result=attempt.test_result,
                question=question,
                defaults={'selected_choice': choice}
            )
        elif key.startswith('multiple_'):
            question_id = int(key.split('_')[1])
            question = get_object_or_404(MultipleChoiceQuestion, id=question_id, test=attempt.test)
            choices = Choice.objects.filter(id__in=request.POST.getlist(key), question=question)
            answer, created = UserMultipleChoiceAnswer.objects.get_or_create(
                test_result=attempt.test_result,
                question=question
            )
            answer.selected_choices.set(choices)
    
    return JsonResponse({'status': 'success'})
