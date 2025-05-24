from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'studentapp'

urlpatterns = [
    path('view_registrations/', views.ViewRegistrationsListView.as_view(), name='view_registrations'),
    path('view_students/', views.ViewEnrollmentListView.as_view(), name='view_students'),
    path('students/<int:stud_id>', views.EachStudentDetailView.as_view(), name='each_student_details'),
    path('enrollment/<int:enrollment_id>/discount/', views.add_discount, name='add_discount'),

]
