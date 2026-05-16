from datetime import timedelta, date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from books.models import Book
from .models import Cart, CartItem, Order, OrderItem, Rental
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt



@login_required(login_url='loginpage')
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_count = cart.items.count()
    return render(request,'cart.html',
        {
            'cart': cart,
            'cart_count': cart_count
        }
    )



@login_required(login_url='loginpage')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book,id=book_id)
    if book.available_stock < 1:
        messages.error(request, "Out of stock.")
        return redirect('book_detail', id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user )
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1
    item, created = CartItem.objects.get_or_create(cart=cart,book=book)
    if not created:
        if item.quantity + quantity <= book.available_stock:
            item.quantity += quantity
        else:
            messages.warning(request,"Exceeds stock limit.")
            return redirect('book_detail',id=book_id)
    else:
        item.quantity = quantity
    item.save()
    messages.success(request,"Cart Updated.")
    return redirect('cart_view')



@login_required(login_url='loginpage')
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user)
    item.delete()
    return redirect('cart_view')



@require_POST
@login_required(login_url='loginpage')
def update_cart_quantity(request):
    item_id = request.POST.get("item_id")
    action = request.POST.get("action")
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    error_message = None

    if action == "increase":
        if item.quantity < item.book.available_stock:
            item.quantity += 1
            item.save()
        else:
            error_message = "Exceeds stock limit."

    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            cart = item.cart
            item.delete()
            return JsonResponse({
                "removed": True,
                "grand_total": cart.get_grand_total(),
                "total_items": cart.items.count()
            })

    return JsonResponse({
        "quantity": item.quantity,
        "subtotal": item.get_total_price(),
        "grand_total": item.cart.get_grand_total(),
        "total_items": item.cart.items.count(),
        "error": error_message
    })




@login_required(login_url='loginpage')
def payment(request):
    cart = get_object_or_404(Cart,user=request.user)
    if not cart.items.exists():
        messages.warning(request,"Your cart is empty.")
        return redirect('cart_view')
    total = 0
    for item in cart.items.all():
        if item.quantity > item.book.available_stock:
            messages.error(request,f"{item.book.title} is out of stock.")
            return redirect('cart_view')
        total += (
            item.book.price
            * item.quantity
        )
    amount_in_paise = int(total * 100)
    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    payment_order = client.order.create({

        "amount": amount_in_paise,

        "currency": "INR",

        "payment_capture": 1

    })
    context = {
        "cart": cart,
        "amount": amount_in_paise,
        "total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": payment_order["id"]
    }
    return render(request,"payment.html",context)


@login_required(login_url='loginpage')
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request,'order_list.html',{'orders': orders})



@login_required(login_url='loginpage')
def rent_book(request, book_id):
    book = get_object_or_404(Book,id=book_id)
    if book.available_stock < 1:
        return redirect('book_detail',id=book_id)
    rental = Rental.objects.create(
        user=request.user,
        book=book,
        due_date=date.today() + timedelta(days=7),
        rent_fee=50.00
    )   
    book.available_stock -= 1
    book.save()
    send_mail(
        subject="Book Rented",
        message=(
            f"You rented '{book.title}'.\n\n"
            f"Return Date : {rental.due_date}\n"
            f"Rent Fee : ₹50"
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=True,
    )
    return redirect('rental_history')




@login_required(login_url='loginpage')
def return_book(request, rental_id):
    rental = get_object_or_404(Rental,id=rental_id,user=request.user)
    if (
        request.method == "POST"
        and rental.status == 'rented'
    ):
        rental.return_date = date.today()
        rental.status = 'returned'     
        rental.current_fine = rental.calculate_fine()
        rental.save()
        rental.book.available_stock += 1
        rental.book.save()
        total_due = (
            rental.current_fine
            + rental.rent_fee
        )
        send_mail(
            subject="Book Returned",
            message=(
                f"Book : {rental.book.title}\n\n"
                f"Return Date : {rental.return_date}\n"
                f"Rent Fee : ₹{rental.rent_fee}\n"
                f"Late Fine : ₹{rental.current_fine}\n\n"
                f"Total Due : ₹{total_due}"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=True,
        )
        messages.success(request,"Book returned successfully.")
        return redirect('fine_payment',rental.id)
    return redirect('rental_history')



@login_required(login_url='loginpage')
def rental_history(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-rent_date')
    for rental in rentals:
        if rental.status == 'rented':
            rental.current_fine = rental.calculate_fine()
            rental.save()
    status = request.GET.get('status')
    if status:
        rentals = rentals.filter(status=status)
    return render( request,'rental_history.html',
        {
            'rentals': rentals,
            'status': status
        }
    )


@login_required(login_url='loginpage')
def mark_lost(request, rental_id):
    rental = get_object_or_404(Rental,id=rental_id,user=request.user)
    if rental.status == 'rented':
        rental.status = 'lost'
        rental.return_date = date.today()
        rental.current_fine = (
            rental.book.price + 100
        )
        rental.save()
        total_due = (
            rental.current_fine
            + rental.rent_fee
        )
        send_mail(
            subject="Book Marked as Lost",
            message=(
                f"Book : {rental.book.title}\n\n"
                f"Lost Date : {rental.return_date}\n"
                f"Book Price : ₹{rental.book.price}\n"
                f"Penalty : ₹100\n"
                f"Lost Fine : ₹{rental.current_fine}\n"
                f"Rent Fee : ₹{rental.rent_fee}\n\n"
                f"Total Due : ₹{total_due}"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=True,
        )

        messages.warning(request,"Book marked as lost.")
        return redirect('fine_payment',rental.id)
    return redirect('rental_history')


@login_required(login_url='loginpage')
def fine_payment(request, rental_id):
    rental = get_object_or_404(Rental,id=rental_id,user=request.user)
    total_amount = (
        rental.current_fine
        + rental.rent_fee
    )
    amount_in_paise = int(
        total_amount * 100
    )
    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))
    payment_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": 1
    })
    context = {
        "rental": rental,
        "amount": amount_in_paise,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": payment_order["id"],
        "rental_id": rental.id,
        "total_due": total_amount,
    }
    return render(request,"fine_payment.html",context)


@login_required(login_url='loginpage')
def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))           
            client.utility.verify_payment_signature({
                'razorpay_order_id':
                data['razorpay_order_id'],
                'razorpay_payment_id':
                data['razorpay_payment_id'],
                'razorpay_signature':
                data['razorpay_signature']
            })
            rental = Rental.objects.get(
                id=data['rental_id'],
                user=request.user
            )            
            rental.is_fine_paid = True
            rental.save()
            return JsonResponse({
                "status": "success"
            })
        except Exception as e:
            print("PAYMENT ERROR:", e)
            return JsonResponse({
                "status": "failed"
            })
    return JsonResponse({"status": "invalid"})


@csrf_exempt
@login_required(login_url='loginpage')
def book_payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))

            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return JsonResponse({"status": "failed"})
            total = cart.get_grand_total()
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                status='completed'
            )
            book_details = ""
            for item in cart.items.all():
                subtotal = (
                    item.book.price
                    * item.quantity
                )

                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    price=item.book.price
                )

                book_details += (
                    f"Book Name : {item.book.title}\n"
                    f"Author : {item.book.author}\n"
                    f"Quantity : {item.quantity}\n"
                    f"Price : ₹{item.book.price}\n"
                    f"Subtotal : ₹{subtotal}\n\n"
                )

                item.book.available_stock -= item.quantity
                item.book.save()

            send_mail(
                subject="Online Payment Successful - Order Confirmation",
                message=(
                    f"Hello {request.user.first_name},\n\n"
                    f"Your online payment was successful.\n\n"       
                    f"Purchased Books\n"
                    f"-----------------------------\n\n"
                    f"{book_details}"
                    f"-----------------------------\n"
                    f"Grand Total Paid : ₹{order.total_amount}\n\n"
                    f"Thank you for shopping with us."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            cart.items.all().delete()
            return JsonResponse({"status": "success","order_id": order.id})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "failed"})
    return JsonResponse({"status": "invalid"})

def order_success(request, order_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)
    return render(request, 'success.html', {'order': order})


@login_required(login_url='loginpage')
def checkout(request):
    cart = get_object_or_404(Cart,user=request.user)
    if not cart.items.exists():
        return redirect('cart_view')
    total = cart.get_grand_total()
    amount = int(total * 100)
    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    payment_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    context = {
        "cart": cart,
        "amount": amount,
        "order_id": payment_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'checkout.html', context)