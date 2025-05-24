from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('home/', views.AdminHomeView.as_view(), name='admin_home'),
    path('admin/profile/edit/', views.AdminProfileEdit.as_view(), name='admin_profile'),
    path('admin/profile/view/', views.AdminProfileView.as_view(), name='admin_view'),
]
