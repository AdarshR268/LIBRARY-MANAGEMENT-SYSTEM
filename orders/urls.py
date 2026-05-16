from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('orders/', views.order_list, name='order_list'),
    path('rent/<int:book_id>/', views.rent_book, name='rent_book'),
    path('return/<int:rental_id>/', views.return_book, name='return_book'),
    path('rentals/', views.rental_history, name='rental_history'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('lost/<int:rental_id>/', views.mark_lost, name='mark_lost'),  
    path('fine/<int:rental_id>/', views.fine_payment, name='fine_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('book-payment-success/',views.book_payment_success,name='book_payment_success'),
    path('payment-success/<int:order_id>/',views.order_success,name='order_success'),

        
]