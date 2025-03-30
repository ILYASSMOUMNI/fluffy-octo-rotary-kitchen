# ai_module/urls.py
from django.urls import path
from . import views

app_name = 'ai_module'

urlpatterns = [
    path('suggest-recipes/', views.suggest_recipes_view, name='suggest_recipes'),
    path('recommendations/', views.personalized_recommendations_view, name='recommendations'),
    path('identify-ingredients/', views.identify_ingredients_view, name='identify_ingredients'),
    path('chat/', views.chat_interface_view, name='chat_interface'),
    path('api/chatbot/', views.chatbot_api_view, name='chatbot_api'), # API endpoint for chat
]