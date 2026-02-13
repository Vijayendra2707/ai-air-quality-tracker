from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from dashboard import views   # ✅ Import from app

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    path('', include('dashboard.urls')),
]
