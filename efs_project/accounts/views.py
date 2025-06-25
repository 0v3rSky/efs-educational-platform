from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .models import VerificationCode
from .forms import CustomUserCreationForm

# Create your views here.
def landing_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    context = {
        'login_form': AuthenticationForm(),
        'signup_form': CustomUserCreationForm()
    }
    return render(request, 'accounts/landing_guest.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Деактивируем пользователя до верификации
            user.save()
            
            # Создаем код верификации
            verification = VerificationCode.create_code(user)
            
            # Отправляем email с кодом
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {verification.code}',
                None,  # Используем DEFAULT_FROM_EMAIL
                [user.email],
                fail_silently=False,
            )
            
            return redirect('verify_email')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            verification = VerificationCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if verification.is_valid():
                verification.is_used = True
                verification.save()
                user.is_active = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('main:home')
            else:
                messages.error(request, 'Код недействителен или истек срок его действия')
        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            messages.error(request, 'Неверный код или email')
    
    return render(request, 'accounts/verify_email.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Создаем код верификации
            verification = VerificationCode.create_code(user)
            
            # Отправляем email с кодом
            send_mail(
                'Код подтверждения входа',
                f'Ваш код подтверждения: {verification.code}',
                None,  # Используем DEFAULT_FROM_EMAIL
                [user.email],
                fail_silently=False,
            )
            
            return redirect('verify_login')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def verify_login(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            verification = VerificationCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if verification.is_valid():
                verification.is_used = True
                verification.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Проверяем, является ли пользователь суперюзером и перенаправляем
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return redirect('main:home') # Перенаправление для обычных пользователей
            else:
                messages.error(request, 'Код недействителен или истек срок его действия')
        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            messages.error(request, 'Неверный код или email')
    
    return render(request, 'accounts/verify_login.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

def admin_login(request):
    return render(request, 'accounts/admin_login.html')