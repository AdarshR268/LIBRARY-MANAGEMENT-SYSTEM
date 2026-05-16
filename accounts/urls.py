from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('loginpage', views.loginpage, name='loginpage'),    
    path('login_fun', views.login_fun, name='login_fun'),
    path('adminhome', views.adminhome, name='adminhome'), 
    path('signuppage', views.signuppage, name='signuppage'),
    path('user_sign', views.user_sign, name='user_sign'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('approvalpage', views.approvalpage, name='approvalpage'),
    path('approve/<int:id>', views.approve, name='approve'),
    path('disapprove/<int:id>', views.disapprove, name='disapprove'),
    path('resetpage', views.resetpage, name='resetpage'),
    path('reset_password_fun', views.reset_password_fun, name='reset_password_fun'),
    path('logoutfun', views.logoutfun, name='logoutfun'),
    path('userlist', views.user_list, name='user_list'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('user-history/<int:user_id>/', views.user_history, name='user_history'),
    path('base', views.base, name='base'),
    path('all-rentals/',views.all_rental_history,name='all_rental_history'),
    path('all-purchases/',views.all_purchase_history,name='all_purchase_history'),
    path('admin-notifications/',views.admin_notifications,name='admin_notifications'),
    path('hide-notification/<int:rental_id>/',views.hide_notification,name='hide_notification'),
    path('user-notifications/',views.user_notifications,name='user_notifications'),
    path('hide-user-notification/<int:rental_id>/',views.hide_user_notification,name='hide_user_notification'),



]