from django.urls import path
from . import views

app_name = 'user'  # SET THE NAMESPACE!
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('info/', views.info, name='info'),
    path('activity/', views.activity, name='activity'),
    path('update/', views.update, name='update'),
    path('delete/', views.delete, name='delete'),
    path('<int:user_id>', views.data, name='data'),    
]