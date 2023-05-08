from django.urls import path
from routing import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

app_name = 'routing'

urlpatterns = [
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('route<int:id>/', views.route, name='route'),
    path('zones/', views.zones),
    path('optimise/', views.optimise),
    path('generate/', views.generate),
    path('update/', views.update),
    path('status/', views.status),
    path('route-stats/', views.route_stats),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico')))
]