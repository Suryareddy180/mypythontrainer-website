from django.urls import path
from . import views

app_name = "batchapp"

urlpatterns = [
    path('', views.BatchFormView.as_view(), name='batch'),
    path('batches/', views.BatchListView.as_view(), name='batch_list'),
    path('<int:batch_id>', views.BatchDetailView.as_view(), name='each_batch'),
    path('delete/<int:pk>', views.BatchDelete.as_view(), name='batch_delete'),
    path('edit/<int:pk>', views.BatchEdit.as_view(), name='edit_batch'),
]
