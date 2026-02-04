from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/step-2/', views.register_step_2, name='register_step_2'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('code-verify/', views.code_verify_view, name='code_verify'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('contact/', views.contact_view, name='contact'),

]
