from django.urls import path

from . import views

urlpatterns = [
    path('assign_task/', views.AssignTaskAPI.as_view(), name='assign_task'),
    # path('create_task/', views.CreateTaskAPI.as_view(), name='create_task'),
    path('create_task_new/', views.CreateProjectTaskAPI.as_view(), name='create_task'),
    path('get_all_tasks/', views.GetTasks.as_view(), name='get_all_tasks'),
    path('update_task_status/', views.UpdateTaskStatusAPI.as_view(), name='update_task_status'),
]
