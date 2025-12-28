from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('financeiro/', views.financeiro, name='financeiro'),
    path('dieta/', views.dieta, name='dieta'),
    path('menstruacao/', views.menstruacao, name='menstruacao'),
    path('hidratacao/', views.hidratacao, name='hidratacao'),
    path('gravidez/', views.gravidez, name='gravidez'),
    path('leitura/', views.leitura, name='leitura'),
    path('diario/', views.diario, name='diario'),
    path('delete/<str:model_name>/<int:item_id>/', views.delete_item, name='delete_item'),
    path('hidratacao/reset/', views.reset_hidratacao, name='reset_hidratacao'),
    path('leitura/update/<int:livro_id>/', views.update_livro_status, name='update_livro_status'),
]
