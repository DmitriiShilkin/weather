from django.urls import path, reverse_lazy

from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from .views import (
    BaseRegisterView,
    CustomUserAccountView,
    ActivateView,
    CustomUserUpdateView,
    password_change,
    password_change_done,
)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='sign/login.html'), name='login'),
    path('activate/<str:user>/', ActivateView.as_view(), name='activate'),
    path('logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('signup/', BaseRegisterView.as_view(), name='signup'),
    path('account/', CustomUserAccountView.as_view(), name='account'),
    path('profile/<int:pk>/', CustomUserUpdateView.as_view(), name='profile'),
    path('password_change/', password_change, name='password_change'),
    path('password_change_done/', password_change_done, name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='sign/password/password_reset.html',
        email_template_name='sign/password/email/password_reset_email.html',
        subject_template_name='sign/password/email/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password_reset_done/', PasswordResetDoneView.as_view(
        template_name='sign/password/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='sign/password/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='sign/password/password_reset_complete.html'
    ), name='password_reset_complete'),
]
