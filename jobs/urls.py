
from django.urls import path
from jobs import views

urlpatterns = [
    path('',views.Index.as_view(), name='index'),
    path('jobs-list',views.JobList.as_view(), name='jobs-list'),
    path('jobs-result',views.JobsResultsView.as_view(), name='jobs-result'),
    path('job-detail/<int:pk>',views.JobDetailView.as_view(), name='job-detail'),
    path('job-create',views.JobCreate.as_view(), name='job-create'),
    path('job-update/<int:pk>',views.JobUpdate.as_view(), name='job-update'),
    path('job-delete/<int:pk>',views.JobDelete.as_view(), name='job-delete'),
]

