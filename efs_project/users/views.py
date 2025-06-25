from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Achievement

@login_required
def profile_view(request):
    if request.method == 'POST':
        edit_type = request.POST.get('edit_type')
        if edit_type == 'username':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)
            if u_form.is_valid():
                u_form.save()
                return redirect('profile')
        elif edit_type == 'photo':
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if p_form.is_valid():
                p_form.save()
                return redirect('profile')
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'users/profile.html', {'u_form': u_form, 'p_form': p_form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

def achievements_view(request):
    try:
        # Получаем все достижения пользователя
        user_achievements = request.user.profile.achievements.all()
        
        # Получаем все возможные достижения
        all_achievements = Achievement.objects.all()
        
        context = {
            'user_achievements': user_achievements,
            'all_achievements': all_achievements,
        }
        
        return render(request, 'users/achievements.html', context)
    except Exception as e:
        print(f"Error in achievements view: {e}")
        # В случае ошибки показываем пустую страницу достижений
        return render(request, 'users/achievements.html', {
            'user_achievements': [],
            'all_achievements': [],
        })
