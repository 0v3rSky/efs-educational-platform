from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course, UserCourseCompletion
from tests.models import TestResult

class UserLevel(models.Model):
    LEVEL_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
    ]
    
    level = models.PositiveIntegerField(choices=LEVEL_CHOICES, default=1)
    points = models.PositiveIntegerField(default=0)
    points_to_next_level = models.PositiveIntegerField(default=1000)  # Очки, необходимые для перехода на следующий уровень
    
    def add_points(self, points):
        """Добавляет очки пользователю и проверяет повышение уровня"""
        self.points += points
        while self.points >= self.points_to_next_level:
            self.points -= self.points_to_next_level
            self.level += 1
            self.points_to_next_level = int(self.points_to_next_level * 1.5)  # Увеличиваем требуемые очки для следующего уровня
        self.save()

    def __str__(self):
        return f"Уровень {self.level} - {self.points} очков"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', default='achievements/default.png')
    condition_type = models.CharField(max_length=50, choices=[
        ('courses_completed', 'Завершено курсов'),
        ('tests_completed', 'Завершено тестов'),
        ('all_courses', 'Все курсы пройдены'),
        ('perfect_score', 'Идеальный результат'),
    ])
    condition_value = models.IntegerField(default=0)
    points_reward = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default_avatar.png')
    level = models.OneToOneField(UserLevel, on_delete=models.CASCADE, null=True, blank=True)
    achievements = models.ManyToManyField(Achievement, blank=True, related_name='profiles')

    # avatar = models.ImageField(default='default_avatar.png', upload_to='profile_avatars/')
    def __str__(self):
        return f'{self.user.username} Profile'

    def add_points(self, points):
        print(f"add_points method called with {points} points for user {self.user.username}")
        # Гарантируем, что у пользователя есть уровень перед добавлением очков
        if not self.level:
            print("User has no level. Creating a new one...")
            self.level = UserLevel.objects.create()
            self.save()
            print(f"New level created: {self.level.level}, Points: {self.level.points}")

        initial_points = self.level.points
        self.level.points += points
        print(f"Points updated from {initial_points} to {self.level.points}")

        # Проверяем, достаточно ли очков для перехода на следующий уровень
        if self.level.level == 1 and self.level.points >= self.level.points_to_next_level:
            print(f"Level 1 reached threshold {self.level.points_to_next_level}. Upgrading to level 2.")
            self.level.level = 2
            self.level.points_to_next_level = 2000  # Увеличиваем порог для следующего уровня
            print(f"Level upgraded to {self.level.level}, next threshold {self.level.points_to_next_level}")

        self.level.save()
        print(f"UserLevel object saved. Current level: {self.level.level}, Current points: {self.level.points}")

    def get_new_achievements(self):
        """Получает список новых достижений, которые должен получить пользователь"""
        new_achievements = set()

        # Проверка достижений за курсы
        completed_courses = UserCourseCompletion.objects.filter(user=self.user).count()
        course_achievements = Achievement.objects.filter(
            condition_type='courses_completed',
            condition_value__lte=completed_courses
        )
        new_achievements.update(course_achievements)

        # Проверка достижений за тесты
        completed_tests = TestResult.objects.filter(user=self.user, passed=True).count()
        test_achievements = Achievement.objects.filter(
            condition_type='tests_completed',
            condition_value__lte=completed_tests
        )
        new_achievements.update(test_achievements)

        # Проверка достижения за все курсы
        total_courses = Course.objects.count()
        if completed_courses >= total_courses:
            all_courses_achievement = Achievement.objects.filter(
                condition_type='all_courses'
            ).first()
            if all_courses_achievement:
                new_achievements.add(all_courses_achievement)

        # Проверка достижений за идеальные результаты
        test_results = TestResult.objects.filter(user=self.user)
        perfect_scores = 0
        for result in test_results:
            if result.percent == 100:
                perfect_scores += 1
        
        perfect_achievements = Achievement.objects.filter(
            condition_type='perfect_score',
            condition_value__lte=perfect_scores
        )
        new_achievements.update(perfect_achievements)

        return new_achievements

    def check_achievements(self):
        """Проверяет и обновляет достижения пользователя"""
        try:
            # Получаем текущие достижения
            current_achievements = set(self.achievements.all())
            
            # Получаем новые достижения
            new_achievements = self.get_new_achievements()
            
            # Находим достижения, которые нужно добавить
            achievements_to_add = new_achievements - current_achievements
            
            if achievements_to_add:
                # Добавляем новые достижения
                self.achievements.add(*achievements_to_add)
                
                # Обновляем очки профиля
                if hasattr(self, 'level'):
                    total_achievement_points = sum(achievement.points_reward for achievement in self.achievements.all())
                    self.level.points = total_achievement_points
                    self.level.save()
        except Exception as e:
            print(f"Error checking achievements: {e}")
            # В случае ошибки просто возвращаем текущие достижения
            return self.achievements.all()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        level = UserLevel.objects.create()
        Profile.objects.create(user=instance, level=level)
    # else:
    #     # Эта часть теперь обрабатывается в add_points
    #     if not instance.profile.level:
    #         level = UserLevel.objects.create()
    #         instance.profile.level = level
    #         instance.profile.save()
    # instance.profile.save() # Удаляем двойное сохранение
    pass # Оставляем сигнал, но основная логика создания уровня перенесена
