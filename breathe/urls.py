from django.urls import path
from . import views

app_name = 'breathe'

urlpatterns = [
    path('', views.category_list_view, name='categories'),
    path('<int:category_id>/', views.technique_list_view, name='techniques'),
    path('technique/<int:technique_id>/', views.technique_detail_view, name='technique'),
    path('guide/<int:technique_id>/', views.guide_view, name='guide'),
    path('api/session/', views.session_manage, name='session_manage'),
]

