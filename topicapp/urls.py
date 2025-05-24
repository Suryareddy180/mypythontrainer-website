from django.urls import path
from . import views

app_name = "topicapp"
urlpatterns = [
    path('', views.TopicFormView.as_view(), name='topic'),
    path('topics/', views.TopicListView.as_view(), name='topic_list'),
    path('<int:topic_id>', views.TopicDetailView.as_view(), name='each_topic'),
    path('toggle-status/<int:pk>/', views.TopicToggleStatus.as_view(), name='topic_toggle_status'),
]


