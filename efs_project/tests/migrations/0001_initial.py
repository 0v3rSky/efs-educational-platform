# Generated by Django 5.2.1 on 2025-06-03 18:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MultipleChoiceQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('points', models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='SingleChoiceQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('points', models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='tests/')),
                ('category', models.CharField(choices=[('Финансовая грамотность', 'Финансовая грамотность'), ('Экономика', 'Экономика'), ('Фондовый рынок', 'Фондовый рынок')], max_length=50)),
                ('difficulty', models.CharField(choices=[('Легкий', 'Легкий'), ('Средний', 'Средний'), ('Сложный', 'Сложный')], max_length=20)),
                ('points', models.PositiveIntegerField(default=50, help_text='Очки, которые получает пользователь за успешное прохождение теста')),
                ('passing_score', models.PositiveIntegerField(default=70, help_text='Минимальный процент правильных ответов для прохождения теста')),
                ('time_limit', models.PositiveIntegerField(default=30, help_text='Время на прохождение теста в минутах')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300)),
                ('is_correct', models.BooleanField(default=False)),
                ('question_multiple', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='tests.multiplechoicequestion')),
                ('question_single', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='tests.singlechoicequestion')),
            ],
        ),
        migrations.AddField(
            model_name='singlechoicequestion',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='single_choice_questions', to='tests.test'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='multiple_choice_questions', to='tests.test'),
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(default=0, help_text='Набранные очки за тест')),
                ('passed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['completed_at'],
            },
        ),
        migrations.CreateModel(
            name='TextQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('points', models.PositiveIntegerField(default=1, help_text='Очки за правильный ответ на этот вопрос')),
                ('correct_answer', models.CharField(max_length=500)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='text_questions', to='tests.test')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='UserMultipleChoiceAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.multiplechoicequestion')),
                ('selected_choices', models.ManyToManyField(to='tests.choice')),
                ('test_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='multiple_choice_answers', to='tests.testresult')),
            ],
        ),
        migrations.CreateModel(
            name='UserSingleChoiceAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.singlechoicequestion')),
                ('selected_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.choice')),
                ('test_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='single_choice_answers', to='tests.testresult')),
            ],
        ),
        migrations.CreateModel(
            name='UserTextAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(blank=True, max_length=500)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.textquestion')),
                ('test_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='text_answers', to='tests.testresult')),
            ],
        ),
    ]
