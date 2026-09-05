from django.urls import path
from workflows import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create/', views.workflow_create_view, name='workflow_create'),
    path('<uuid:workflow_id>/edit/', views.workflow_edit_view, name='workflow_edit'),
    path('<uuid:workflow_id>/delete/', views.workflow_delete_view, name='workflow_delete'),
    path('<uuid:workflow_id>/run/', views.workflow_run_view, name='workflow_run'),
    path('<uuid:workflow_id>/node/create/', views.node_create_view, name='node_create'),
    path('node/<uuid:node_id>/edit/', views.node_edit_view, name='node_edit'),
    path('node/<uuid:node_id>/delete/', views.node_delete_view, name='node_delete'),
    path('logs/', views.execution_logs_view, name='execution_logs'),
    path('logs/<uuid:log_id>/', views.execution_log_detail_view, name='execution_log_detail'),
]

