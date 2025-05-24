"""
URL configuration for MyPythonTrainer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userapp.urls', namespace='userapp')),
    path('course/', include('courseapp.urls', namespace='courseapp')),
    path('trainer/', include('trainers.urls', namespace='trainers')),
    path('batch/', include('batchapp.urls', namespace='batchapp')),
    path('student/', include('studentapp.urls',namespace='studentapp')),
    path('admins/', include('adminapp.urls',namespace='adminapp')),
    path('topic/', include('topicapp.urls', namespace='topicapp')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
