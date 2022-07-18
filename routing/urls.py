from django.urls import path
from routing import views

app_name = 'routing'

urlpatterns = [
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('route<int:id>/', views.route, name='route'),
    path('zones/', views.zones),
]