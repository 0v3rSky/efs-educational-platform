from django.shortcuts import render, get_object_or_404, redirect
from .models import Quest, QuestSection, QuestQuiz, QuestQuizQuestion, QuestQuizAnswer, QuestTopic
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

def quest_list(request):
    topics = QuestTopic.objects.prefetch_related('quests').all()
    return render(request, 'quests/quest_list.html', {'topics': topics})

def quest_detail(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    sections = quest.sections.all()
    return render(request, 'quests/quest_detail.html', {
        'quest': quest,
        'sections': sections,
    })

@login_required
def quest_quiz(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    quiz = getattr(quest, 'quiz', None)
    if not quiz:
        return redirect('quests:quest_detail', pk=pk)
    questions = quiz.questions.all()
    if request.method == 'POST':
        # Простейшая обработка (можно доработать)
        user_answers = {str(q.id): request.POST.get(f'q_{q.id}') for q in questions}
        results = []
        score = 0
        for q in questions:
            correct = q.answers.filter(is_correct=True, id=user_answers.get(str(q.id))).exists()
            results.append({'question': q, 'correct': correct})
            if correct:
                score += 1
        
        # Если тест пройден успешно (более 70% правильных ответов), начисляем очки
        if score / questions.count() >= 0.7:
            request.user.profile.add_points(quest.points)
            
        return render(request, 'quests/quest_quiz_result.html', {
            'quest': quest,
            'quiz': quiz,
            'results': results,
            'score': score,
            'total': questions.count(),
        })
    return render(request, 'quests/quest_quiz.html', {
        'quest': quest,
        'quiz': quiz,
        'questions': questions,
    })

def quest_section(request, pk, section_idx):
    quest = get_object_or_404(Quest, pk=pk)
    sections = list(quest.sections.all())
    total = len(sections)
    section_idx = max(0, min(section_idx, total-1))
    section = sections[section_idx]
    prev_idx = section_idx - 1 if section_idx > 0 else None
    next_idx = section_idx + 1 if section_idx < total-1 else None
    return render(request, 'quests/quest_section.html', {
        'quest': quest,
        'section': section,
        'section_idx': section_idx,
        'total': total,
        'prev_idx': prev_idx,
        'next_idx': next_idx,
    })

def quest_quiz_step(request, pk, step):
    quest = get_object_or_404(Quest, pk=pk)
    quiz = getattr(quest, 'quiz', None)
    if not quiz:
        return redirect('quests:quest_detail', pk=pk)
    questions = list(quiz.questions.all())
    total = len(questions)
    step = max(0, min(step, total-1))
    question = questions[step]
    # Сохраняем ответы в сессии
    if request.method == 'POST':
        user_answers = request.session.get(f'quest_{pk}_quiz_answers', {})
        user_answers[str(question.id)] = request.POST.get('answer')
        request.session[f'quest_{pk}_quiz_answers'] = user_answers
        if step < total-1:
            return redirect('quests:quest_quiz_step', pk=pk, step=step+1)
        else:
            # Показываем результат сразу!
            score = 0
            results = []
            for q in questions:
                correct = q.answers.filter(is_correct=True, id=user_answers.get(str(q.id))).exists()
                results.append({'question': q, 'correct': correct})
                if correct:
                    score += 1
            # Очищаем ответы из сессии
            del request.session[f'quest_{pk}_quiz_answers']
            return render(request, 'quests/quest_quiz_result.html', {
                'quest': quest,
                'quiz': quiz,
                'results': results,
                'score': score,
                'total': total,
            })
    prev_step = step - 1 if step > 0 else None
    next_step = step + 1 if step < total-1 else None
    user_answers = request.session.get(f'quest_{pk}_quiz_answers', {})
    selected = user_answers.get(str(question.id))
    return render(request, 'quests/quest_quiz_step.html', {
        'quest': quest,
        'quiz': quiz,
        'question': question,
        'step': step,
        'total': total,
        'prev_step': prev_step,
        'next_step': next_step,
        'selected': selected,
    })

def get_quests_by_topic(request, topic_id):
    topic = QuestTopic.objects.get(id=topic_id)
    quests = topic.quests.all()
    data = [
        {
            'id': q.id,
            'title': q.title,
            'description': q.description,
            'image_url': q.image.url if q.image else '',
        } for q in quests
    ]
    return JsonResponse({'quests': data, 'topic': topic.name})
