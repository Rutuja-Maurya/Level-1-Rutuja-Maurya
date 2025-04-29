from django.urls import path
from . import views

urlpatterns = [
    path('', views.pricing_config_list, name='pricing_config_list'),
    path('create/', views.pricing_config_create, name='pricing_config_create'),
    path('<int:pk>/', views.pricing_config_detail, name='pricing_config_detail'),
    path('<int:pk>/edit/', views.pricing_config_edit, name='pricing_config_edit'),
    path('<int:pk>/delete/', views.pricing_config_delete, name='pricing_config_delete'),
    path('calculator/', views.price_calculator, name='price_calculator'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
] 