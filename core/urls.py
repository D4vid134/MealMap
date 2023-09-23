from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dining_diary/', views.dining_diary, name='dining_diary'),
    path('update_times_eaten/<int:data_id>/', views.update_times_eaten, name='update_times_eaten'),
    path('update_rating/<int:data_id>/', views.update_rating, name='update_rating'),
    path('update_comment/<int:data_id>/', views.update_comment, name='update_comment'),
    path('update_is_favorite/<int:data_id>/', views.update_is_favorite, name='update_is_favorite'),
    path('update_favorite_dish/<int:data_id>/', views.update_favorite_dish, name='update_favorite_dish'),
    path('delete_user_restaurant/<int:data_id>/', views.delete_user_restaurant, name='delete_user_restaurant'),
    path('random_restaurant_finder/', views.random_restaurant_finder, name='random_restaurant_finder'),
    path('fetch_restaurant_details/<str:place_id>/', views.fetch_restaurant_details, name='fetch_restaurant_details'),
    
    
    # path('nearby_restaurant_generator/', views.nearby_restaurant_generator, name='nearby_restaurant_generator')
]