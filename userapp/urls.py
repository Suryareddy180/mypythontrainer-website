# userapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'userapp'
urlpatterns = [
    path('adminregistration/', views.RegisterAdminView.as_view(), name='register-admin'),
    path('logout/', auth_views.LogoutView.as_view(template_name='userapp/logout.html'), name='logout'),
    path('no-access/', views.TemplateView.as_view(template_name='userapp/no_access.html'), name='no-access'),

    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('', views.NewIndexPageView.as_view(), name='home'),  # Home URL for students
    # path('home/', views.IndexPageView.as_view(), name='index_page'),  # Home URL for students
    # path('about/', views.AboutPageView.as_view(), name='about_page'),
    # path('contact/', views.ContactView.as_view(), name='contact'),
    path('my-enrolled-courses/', views.AppliedCoursesView.as_view(), name='applied_courses'),
    path('user/profile/view', views.UserProfileView.as_view(), name='user_profile_view'),
    path('user/profile/edit', views.UserProfileEdit.as_view(), name='user_profile_edit'),

    path('view/', views.CourseListView.as_view(), name='course_view'),
    path('<int:course_id>', views.CourseDetailView.as_view(), name='each_course'),
    # path('registration/<str:course_title>/', views.CourseRegistration.as_view(), name='course_regs'),

    # JC - New UI
    path('home/', views.NewIndexPageView.as_view(), name='new_index_page'),
    path('trainers/', views.NewAboutPageView.as_view(), name='new_about_page'),
    path('courses/', views.NewCoursesPageView.as_view(), name='new_courses_page'),
    path('course-calendar/', views.NewCourseCalendarPageView.as_view(), name='new_courses_calendar_page'),
    path('stories/', views.NewStoriesPageView.as_view(), name='new_stories_page'),
    path('contact/', views.NewContactPageView.as_view(), name='new_contact_page'),
    path('privacy-policy/', views.PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('terms-conditions/', views.TermsConditionsPageView.as_view(), name='terms_conditions'),
    path('refund-policy/', views.RefundPolicyPageView.as_view(), name='refund_policy'),
    path('register/', views.NewRegistrationPageView.as_view(), name='new_registration_page'),
    path('login/', views.NewLoginPageView.as_view(), name='login'),
    path('payment/proceed/<int:course_id>/<str:payment_type>/', views.MakePaymentView.as_view(), name='make_payment'),
    path('course/enroll/<str:course_title>/<str:batch_name>', views.EnrollCourse.as_view(), name='new_course_enrollment'),
    path('confirm_enrollment/<str:course_title>/<str:batch_name>/', views.ConfirmEnrollCourse.as_view(), name='confirm_enrollment'),
    path('payment/verify/', views.PaymentVerificationView.as_view(), name='payment_verification'),
    path('payment/failed/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('batch/details/<str:batch_number>', views.BatchDetailView.as_view(), name='batch_details'),
    path('feedback/',views.CourseFeedbackCreateView.as_view(),name='feedback'),
    path('feedbackSuccess/',views.FeedbackSuccessView.as_view(),name='feedback-success'),
    path('feedbackList/',views.CourseFeedbackListView.as_view(),name='feedback-List'),
]
