from django.urls import path
from . import views

app_name = "trainers"
urlpatterns = [
    path('', views.TrainerFormView.as_view(), name='trainer_create'),
    path('trainers/', views.TrainersListView.as_view(), name='trainer_view'),
    path('Degree/', views.DegreeView.as_view(), name='Degree'),
    path('DegreeAdd/', views.DegreeAdd.as_view(), name='DegreeAdd'),
    path('DegreeSuccess/', views.DegreeSuccess.as_view(), name='DegreeSuccess'),
    path('DegreeList/', views.DegreeList.as_view(), name='DegreeList'),
    path('College/', views.CollegeView.as_view(), name='College'),
    path('CollegeAdd/', views.CollegeAdd.as_view(), name='CollegeAdd'),
    path('CollegeSuccess/', views.CollegeSuccess.as_view(), name='CollegeSuccess'),
    path('CollegeList/', views.CollegeList.as_view(), name='CollegeList'),
    path('Qualification/', views.QualificationsView.as_view(), name='Qualification'),
    path('QualificationAdd/', views.QualificationAdd.as_view(), name='QualificationAdd'),
    path('QualificationSuccess/', views.QualificationSuccess.as_view(), name='QualificationSuccess'),
    path('QualificationList/', views.QualificationList.as_view(), name='QualificationList'),
    path('Organization/', views.OrganizationView.as_view(), name='Organization'),
    path('OrganizationAdd/', views.OrganizationAdd.as_view(), name='OrganizationAdd'),
    path('OrganizationSuccess/', views.OrganizationSuccess.as_view(), name='OrganizationSuccess'),
    path('OrganizationList/', views.OrganizationList.as_view(), name='OrganizationList'),
    path('Award/', views.AwardsView.as_view(), name='Award'),
    path('AwardAdd/', views.AwardAdd.as_view(), name='AwardAdd'),
    path('AwardSuccess/', views.AwardSuccess.as_view(), name='AwardSuccess'),
    path('AwardList/', views.AwardList.as_view(), name='AwardList'),
    path('<int:trainer_id>', views.TrainerDetailView.as_view(), name='trainer_one'),
    path('toggle-status/<int:pk>/', views.TrainerToggleStatus.as_view(), name='trainer_toggle_status'),
    path('stories/',views.CourseFeedbackListView.as_view(),name='stories'),
    path('feedback/approve/<int:feedback_id>/', views.approve_feedback, name='approve_feedback'),
    path('feedback/reject/<int:feedback_id>/', views.reject_feedback, name='reject_feedback'),

]
