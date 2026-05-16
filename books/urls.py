from django.urls import path
from . import views

urlpatterns = [
    
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('admin/books/', views.admin_book_list, name='admin_book_list'),
    path('admin/books/add/', views.addbook, name='add_book'),
    path('admin/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('admin/books/delete/<int:id>/', views.delete_book, name='delete_book'),
    
    

]