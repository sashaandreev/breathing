from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('api/activity/tap/', views.activity_tap, name='activity_tap'),
]

