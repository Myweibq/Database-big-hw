from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('settings', views.settings, name='settings'),
    path('search', views.search, name='search'),
    path('upload', views.upload, name='upload'),
    path('logout', views.logout, name='logout'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('like-post', views.like_post, name='like-post'),
    path('about', views.about, name='about'),
    path('nodelete', views.nodelete, name='nodelete'),
    path('delete/<uuid:post_id>/', views.delete_post, name='delete_post'),
]
