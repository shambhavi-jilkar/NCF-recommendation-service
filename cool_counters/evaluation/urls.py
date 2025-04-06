from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    path('', views.home, name='home'),
    path('evaluate/', views.evaluate, name='evaluate'),
    path('health/', views.health, name='health'),
]
