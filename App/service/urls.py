from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'service'  # SET THE NAMESPACE!
urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),
    path('detail/<int:post_id>', views.detail, name='detail'),
    path('update/<int:post_id>', views.update, name='update'),
    path('close/<int:post_id>', views.close, name='close'), 
    path('delete/<int:post_id>', views.delete, name='delete'),

    path('<int:post_id>/comment/create/', views.create_comment, name='create-comment'),
]