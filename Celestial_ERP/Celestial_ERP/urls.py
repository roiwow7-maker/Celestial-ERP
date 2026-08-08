"""
URL configuration for Celestial_ERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path, re_path

from Applet import views as applet_views

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', applet_views.root, name='root'),
    path('applet/', include('Applet.urls')),
    path('asistencia/', include('Attendance.urls')),
    path('contabilidad/', include('Accounting.urls')),
    path('inventario/', include('Inventory.urls')),
    path('comercio/', include('Commerce.urls')),
    path('api/', include('ERP_api.urls')),
    path('', include('DATA_scope.urls')),
    path('admin/', admin.site.urls),
]

if settings.SERVE_STATIC_LOCALLY:
    urlpatterns.append(
        re_path(r"^static/(?P<path>.*)$", serve_static, {"insecure": True})
    )
