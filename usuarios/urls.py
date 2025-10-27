from django.urls import path
from django.contrib.auth import views as auth_views
#se ocupara para el recuperar contraseña pero por el momento no se usa
from usuarios.views import (registrarse, iniciar_sesion, logout_view, recuperar_contraseña, crear_nueva_contraseña, modulo_usuarios, eliminar_usuario, editar_usuario)

urlpatterns = [
    path("registrarse/", registrarse, name='registrarse'),
    path("recuperar_contraseña/", recuperar_contraseña, name='recuperar_contraseña'),
    path("crear_nueva_contraseña/", crear_nueva_contraseña, name='crear_nueva_contraseña'),
    path('usuarios/', modulo_usuarios, name='modulo_usuarios'),
    path("iniciar_sesion/", iniciar_sesion, name='iniciar_sesion'),
    path('eliminar_usuario/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path("logout/", logout_view, name='logout'),

    # Cambiar contraseña (usuario logueado)
    path("password/change/", auth_views.PasswordChangeView.as_view(
        template_name="usuarios/password_change_form.html",
        success_url="/usuarios/password/change/done/"
    ), name="password_change"),

    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="usuarios/password_change_done.html"
    ), name="password_change_done"),

    # Recuperar contraseña (flujo por email)
    path("password/reset/", auth_views.PasswordResetView.as_view(
        template_name="usuarios/password_reset_form.html",
        email_template_name="usuarios/email/password_reset_email.txt",
        subject_template_name="usuarios/email/password_reset_subject.txt",
        success_url="/usuarios/password/reset/done/"
    ), name="password_reset"),

    path("password/reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="usuarios/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="usuarios/password_reset_confirm.html",
        success_url="/usuarios/reset/complete/"
    ), name="password_reset_confirm"),

    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="usuarios/password_reset_complete.html"
    ), name="password_reset_complete"),
]
