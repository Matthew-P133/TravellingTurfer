from django.urls import path
from routing import views

app_name = 'routing'

urlpatterns = [
    path('', views.map, name='map'),
    path('map', views.map, name='map'),
    path('route<int:id>/', views.route),
]