from django.urls import path, re_path
from . import views

urlpatterns = [
    # Legacy SQL endpoint
    path('query/', views.query_endpoint, name='query_endpoint'),
    
    # Health & stats
    path('health/', views.health_check, name='health'),
    path('stats/', views.get_stats, name='stats'),
    
    # Table operations
    path('tables/', views.list_tables, name='list_tables'),
    path('tables/<str:table_name>/', views.get_table_schema, name='get_table_schema'),
    path('tables/<str:table_name>/rows/', views.get_table_rows, name='get_table_rows'),
    path('tables/<str:table_name>/rows/new/', views.insert_row, name='insert_row'),
    re_path(r'^tables/(?P<table_name>\w+)/rows/(?P<row_id>\d+)/$', views.delete_row, name='delete_row'),
    
    # Query execution
    path('query/execute/', views.execute_query, name='execute_query'),
    path('reset/', views.reset_database, name='reset_database'),
]
