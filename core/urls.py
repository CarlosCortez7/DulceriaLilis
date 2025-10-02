"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
<<<<<<< HEAD
from usuarios import views

=======
from productos.views import home, agregar_producto  
from usuarios.views import registrarse, iniciar_sesion, cerrar_sesion, tareas, tasks_completed, crear_tarea, tareas_detalles, tarea_completada, tarea_eliminada
>>>>>>> e8be2a1 (semillas y modulo categoria + formularios)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('compras/', include('compras.urls')),  

<<<<<<< HEAD
    path("", views.home, name='home'),
    path("registrarse/", views.registrarse, name='registrarse'),
    path("tareas/", views.tareas, name='tareas'),
    path("tasks_completed/", views.tasks_completed, name='tasks_completed'),
    path("tareas/crear/", views.crear_tarea, name='crear_tarea'),
    path("tareas/<int:tarea_id>/", views.tareas_detalles, name='tareas_detalles'),
    path("tareas/<int:tarea_id>/completado", views.tarea_completada, name='tarea_completada'),
    path("tareas/<int:tarea_id>/eliminar", views.tarea_eliminada, name='tarea_eliminada'),

    path("iniciar_sesion/", views.iniciar_sesion, name='iniciar_sesion'),
    path("logout/", views.cerrar_sesion, name='logout'),


]
=======
    path("", home, name='home'),
    path("agregar_producto/", agregar_producto, name='agregar_producto'),
    path("registrarse/", registrarse, name='registrarse'),
    path("tareas/", tareas, name='tareas'),
    path("tasks_completed/", tasks_completed, name='tasks_completed'),
    path("tareas/crear/", crear_tarea, name='crear_tarea'),
    path("tareas/<int:tarea_id>/", tareas_detalles, name='tareas_detalles'),
    path("tareas/<int:tarea_id>/completado", tarea_completada, name='tarea_completada'),
    path("tareas/<int:tarea_id>/eliminar", tarea_eliminada, name='tarea_eliminada'),

    path("iniciar_sesion/", iniciar_sesion, name='iniciar_sesion'),
    path("logout/", cerrar_sesion, name='logout'),
]
>>>>>>> e8be2a1 (semillas y modulo categoria + formularios)
