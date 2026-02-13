from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('health/', views.health_page),
    path('route/', views.route_page),
    path('indoor/', views.indoor_page),

    path('api/aqi/', views.aqi_api),
    path('api/history/', views.history_api),
    path("api/heatmap/", views.heatmap_api),
    path('api/health/', views.health_api),
    path("api/smart-route/", views.smart_route_api),
    path('api/indoor/', views.indoor_api),
    path('compare/', views.compare_page),
    path('api/compare/', views.compare_api),
    path('api/current-aqi/', views.current_aqi_api),
]
