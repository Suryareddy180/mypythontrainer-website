from django.urls import path
from . import views

app_name = "courseapp"

urlpatterns = [
    path('', views.CoursesFormView.as_view(), name='course_create'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('<int:course_id>', views.CourseDetailView.as_view(), name='each_courses'),
    path('toggle-status/<int:pk>/', views.CourseToggleStatus.as_view(), name='course_toggle_status'),
]
