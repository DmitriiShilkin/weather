import random
from string import hexdigits

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from .forms import BaseRegisterForm, CustomUserUpdateForm
from .models import CustomUser, OneTimeCode
from .services import send_one_time_code


# Представление для регистрации пользователя
class BaseRegisterView(CreateView):
    model = CustomUser
    form_class = BaseRegisterForm
    template_name = 'sign/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BaseRegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            common_group = Group.objects.get(name='common')
            common_group.user_set.add(user)
            return redirect('activate', request.POST['username'])
        else:
            return render(request, self.template_name, {'form': form})


# Представление для активации зарегистрированного пользователя по коду на почту
class ActivateView(CreateView):
    template_name = 'sign/activate.html'

    def get_context_data(self, **kwargs):
        user_ = self.kwargs.get('user')
        one_time_code = OneTimeCode.objects.filter(user=user_).first()
        if one_time_code and one_time_code.is_expired():
            one_time_code.delete()
            one_time_code = None
        if not one_time_code:
            code = ''.join(random.sample(hexdigits, 5))
            OneTimeCode.objects.create(user=user_, code=code)
            user = CustomUser.objects.get(username=user_)
            send_one_time_code(code, user)

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = request.path.split('/')[-2]
            one_time_code = OneTimeCode.objects.filter(code=request.POST['code'], user=user).first()
            if one_time_code:
                if not one_time_code.is_expired():
                    CustomUser.objects.filter(username=user).update(is_active=True)
                    one_time_code.delete()
                    return redirect('login')
                else:
                    return render(self.request, 'sign/expired_code.html')
            else:
                data = {
                    'code': request.POST['code'],
                    'user': user,
                }
                return render(self.request, 'sign/invalid_code.html', context=data)


class CustomUserUpdateView(PermissionRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'sign/customuser_update.html'
    success_url = reverse_lazy('index')
    permission_required = ('sign.change_customuser',)
    raise_exception = True

    def get_permission_required(self):
        self.object = self.get_object()
        if not (
                self.request.user == self.object or
                self.request.user.is_superuser
        ):
            content = f'''
                <p style="font-size: 2em; font-weight: bold; font-family: Times New Roman;">403 Forbidden</p>
            '''
            return HttpResponse(content=content)
        if self.permission_required is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the "
                f"permission_required attribute. Define "
                f"{self.__class__.__name__}.permission_required, or override "
                f"{self.__class__.__name__}.get_permission_required()."
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # To keep the user logged in
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'sign/password/password_change.html', {'form': form})


@login_required
def password_change_done(request):
    return render(request, 'sign/password/password_change_done.html')


class CustomUserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'sign/account.html'
