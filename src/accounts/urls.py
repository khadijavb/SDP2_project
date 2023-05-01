from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('az/', views.azPage),
    path('rus/', views.rusPage),
    path('eng/', views.engPage),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('hone/', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('save_results/', views.save_results, name='save_results'),
    path('saved_results/', views.view_saved_results, name='view_saved_results'),
    path('clear_history/', views.clear_history, name='clear_history'),
    path('help/', views.help_page, name='help'),
    path('search/', views.search, name='search'),
    path('zero_result/', views.zero_result, name='zero_result'),
    path('contact/', views.contact_page, name='contact'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
