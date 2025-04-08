from django.urls import path
from . import views


urlpatterns = [
    path('AdminLogin/',views.AdminLogin, name='AdminLogin'),
    path("AdminLoginCheck/", views.AdminLoginCheck, name="AdminLoginCheck"),
    path("AdminHome/", views.AdminHome, name="AdminHome"),
    path('RegisterUsersView/', views.RegisterUsersView, name='RegisterUsersView'),
    path('activate_user/',views.activate_user,name = 'activate_user'),
    path('BlockUser/', views.BlockUser, name='BlockUser'),
    path('UnblockUser-user/', views.UnblockUser, name='UnblockUser'),
    path('add_route/', views.add_route, name='add_route'),
    path('route/edit/<int:pk>/',views.edit_route, name='edit_route'),
    path('route/delete/<int:pk>/',views.delete_route, name='delete_route'),
    path('viewroutes/',views.viewroutes,name = 'viewroutes'),
    path('bus-pass-applied-users/', views.BusPassAppliedUsersView, name='bus_pass_applied_users'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),
    
]