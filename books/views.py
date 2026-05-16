
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import auth
from django.db.models import Q
import os,re,random
from django.contrib.auth.decorators import login_required
from books.models import Book
from orders.models import Rental,CartItem
from datetime import date


@login_required(login_url='loginpage')
def addbook(request):
    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        publisher = request.POST.get('publisher')
        price = request.POST.get('price')
        description = request.POST.get('description')
        try:
            stock = int(request.POST.get('stock', 0))
        except ValueError:
            stock = 0
        image = request.FILES.get('cover_image')
        if Book.objects.filter(title__iexact=title).exists():

            messages.error(
                request,
                "Book with this title already exists."
            )
            return render(request, 'add_book.html')   
        Book.objects.create(

            title=title,
            author=author,
            publisher=publisher,
            price=price,
            description=description,
            cover_image=image,

            stock=stock,

            available_stock=stock)
        messages.success(request,"Book added successfully.")
        return redirect('admin_book_list')
    return render(request, 'add_book.html')




@login_required(login_url='loginpage')
def admin_book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})



@login_required(login_url='loginpage')
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        title = request.POST.get('title')
        if Book.objects.filter(title__iexact=title).exclude(id=book.id).exists():
            messages.error(
                request,
                "Book with this title already exists."
            )
            return render(request, 'edit_book.html', {
                'book': book
            })
        book.title = title
        book.author = request.POST.get('author')
        book.publisher = request.POST.get('publisher')
        book.price = request.POST.get('price')
        book.description = request.POST.get('description')
        try:
            book.stock = int(request.POST.get('stock', 0))
        except ValueError:
            book.stock = 0
        book.available_stock = book.stock
        if request.FILES.get('cover_image'):
            if book.cover_image and os.path.isfile(book.cover_image.path):
                os.remove(book.cover_image.path)
            book.cover_image = request.FILES.get('cover_image')
        book.save()
        messages.success(request,"Book updated successfully!")
        return redirect('admin_book_list')
    return render(request, 'edit_book.html', {'book': book})

@login_required(login_url='loginpage')
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)     
    if book.cover_image and os.path.isfile(book.cover_image.path):
        os.remove(book.cover_image.path)       
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect('admin_book_list')




@login_required(login_url='loginpage')
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    already_rented = False
    cart_count = 0
    if request.user.is_authenticated:

        already_rented = Rental.objects.filter(
            user=request.user,
            book=book,
            status='rented'
        ).exists()

        cart_count = CartItem.objects.filter(
            cart__user=request.user
        ).count()
    context = {
        'book': book,
        'already_rented': already_rented,
        'cart_count': cart_count
    }
    return render(request,'book_detail.html',context)



