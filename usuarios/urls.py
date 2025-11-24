from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios import views

urlpatterns = [
    # --- Accesos Básicos ---
    path("registrarse/", views.registrarse, name='registrarse'),
    path("iniciar_sesion/", views.iniciar_sesion, name='iniciar_sesion'),
    path("logout/", views.logout_view, name='logout'),

    # --- NUEVA RUTA DE CAMBIO DE CLAVE (Reemplaza al perfil) ---
    # Corrección: Agregado 'views.' antes del nombre de la función
    path('seguridad/cambiar-password/', views.cambiar_password_dedicado, name='cambiar_password_dedicado'),
    path('usuarios/reset-password/<int:user_id>/', views.resetear_password_admin, name='resetear_password_admin'),
    

    # --- CRUD Usuarios ---
    path('usuarios/', views.modulo_usuarios, name='modulo_usuarios'),
    path('usuarios/exportar/', views.exportar_excel_usuarios, name='exportar_excel_usuarios'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path("crear_nueva_contrasena/", views.crear_nueva_contrasena, name='crear_nueva_contrasena'),

    # --- Recuperación de contraseña (flujo completo por email) ---
    path("recuperar_contrasena/", auth_views.PasswordResetView.as_view(
        template_name="usuarios/recuperar_contrasena.html",
        email_template_name="usuarios/email/password_reset_email.txt",
        subject_template_name="usuarios/email/password_reset_subject.txt",
        success_url="/usuarios/password/reset/done/"
    ), name="recuperar_contrasena"),

    path("password/reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="usuarios/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(
        template_name="usuarios/password_reset_confirm.html",
        success_url="/usuarios/reset/complete/"
    ), name="password_reset_confirm"),

    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="usuarios/password_reset_complete.html"
    ), name="password_reset_complete"),

    # --- Otros ---
    path('sin_permiso/', views.sin_permiso, name='sin_permiso'),

    # (Opcional) Cambio de contraseña genérico de Django
    # Nota: Ya tienes tu propia vista dedicada arriba, pero puedes dejar estas si quieres
    path("password/change/", auth_views.PasswordChangeView.as_view(
        template_name="usuarios/password_change_form.html",
        success_url="/usuarios/password/change/done/"
    ), name="password_change"),

    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="usuarios/password_change_done.html"
    ), name="password_change_done"),
]