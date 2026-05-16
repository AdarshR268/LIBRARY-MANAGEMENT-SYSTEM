from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from orders.models import Rental, Order,OrderItem,CartItem
from books.models import Book
from datetime import date
import random, os, re
from django.http import JsonResponse

# Create your views here.

def homepage(request):
    books = Book.objects.all()
    return render(request, 'homepage.html', {'books': books})


@login_required(login_url='loginpage')  
def adminhome(request):
    overdue_data = overdue_alerts(request)
    pnd = CustomUser.objects.filter(
        status='0'
    ).count()
    pend = max(0, pnd - 1)   
    hidden_notifications = request.session.get(
        'hidden_notifications',
        []
    )    
    overdue_count = Rental.objects.filter(
        status='rented',
        due_date__lt=date.today()
    ).exclude(
        id__in=hidden_notifications
    ).count()

    context = {
        'pending': pend,
        'overdue_count': overdue_count,
        **overdue_data
    }
    return render(request,'adminhome.html',context)   



@login_required(login_url='loginpage')
def base(request):
    overdue_data = overdue_alerts(request)
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )
    else:

        books = Book.objects.all()
    cart_count = 0
    user_overdue_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(
            cart__user=request.user
        ).count()
        hidden_user_notifications = request.session.get(
            'hidden_user_notifications',
            []
        )
        user_overdue_count = Rental.objects.filter(
            user=request.user,
            status='rented',
            due_date__lt=date.today()
        ).exclude(
            id__in=hidden_user_notifications
        ).count()
    context = {
        'books': books,
        'cart_count': cart_count,
        'query': query,
        'user_overdue_count': user_overdue_count,
        **overdue_data
    }
    return render(request,'base.html',context)

def loginpage(request):
    return render(request, 'loginpage.html')


def signuppage(request):
    return render(request, 'signuppage.html')


def login_fun(request):
    if request.method == 'POST':  
        username = request.POST['usname']
        password = request.POST['pass']        
        user = auth.authenticate(username=username, password=password)       
        if user is not None:
            if user.is_authenticated:  
                if user.is_staff:
                    login(request, user)
                    request.session['user'] = user.username  
                    return redirect('adminhome')
                else:
                    login(request, user)
                    request.session['user'] = user.username  
                    
                    return redirect('base')            
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('loginpage')
    return render(request, 'loginpage.html')



def user_sign(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname').strip()
        last_name = request.POST.get('lname').strip()
        user_name = request.POST.get('uname').strip()  
        email = request.POST.get('email').strip().lower()
        age = request.POST.get('age')
        phone = request.POST.get('phone').strip()
        address = request.POST.get('address').strip()
        image = request.FILES.get('image')  
        us=request.POST['usr']          
        if CustomUser.objects.filter(username=user_name).exists():
            messages.error(request, 'This username already exists')
            return redirect('signuppage')     
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered')
            return redirect('signuppage')   
        if not re.match(r'^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@(gmail\.com)$', email):
            messages.error(request, 'Enter a valid Gmail address (example@gmail.com)')
            return redirect('signuppage')     
        if not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Phone number must be exactly 10 digits')
            return redirect('signuppage')      
        if CustomUser.objects.filter(Phone_number=phone).exists():
            messages.error(request, 'Phone number already exists')
            return redirect('signuppage')      
        user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=user_name,           
            email=email,
            image=image,
            Age=age,
            address=address,
            Phone_number=phone,
            status=us
        )    
        user.save()
        subject = 'Registration confirmation'
        message = 'Registration is success, please wait for admin approval...'
        send_mail(subject,"Hello " + user_name + ' ' + message,settings.EMAIL_HOST_USER,{email})
        messages.success(request, 'User registration success. Please wait for admin approval..')
        return redirect('signuppage')


def aboutus(request):
    return render(request, 'aboutus.html')  


@login_required(login_url='loginpage')
def approvalpage(request):
    users = CustomUser.objects.filter(~Q(is_staff=True))
    return render(request,'approvalpage.html',
        {
            'user': users
        }
    )


@login_required(login_url='loginpage')
def approve(request, id):
    if not request.user.is_staff:
        messages.error(request,"Access denied.")
        return redirect('loginpage')
    usr = get_object_or_404(CustomUser,id=id)
    if not usr.is_staff:
        usr.status = '1'
        password = str(random.randint(100000, 999999))
        usr.set_password(password)
        usr.save()
        subject = 'Admin Approved'
        message = (
            f"Username : {usr.username}\n"
            f"Password : {password}\n"
            f"Email : {usr.email}"
        )
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [usr.email]
        )
        messages.success(request,'User approved successfully.')
    return redirect('approvalpage')


@login_required(login_url='loginpage')
def disapprove(request, id):
    if not request.user.is_staff:
        messages.error(request,"Access denied.")
        return redirect('loginpage')
    usr = get_object_or_404(CustomUser,id=id)
    if not usr.is_staff:
        usr.status = '2'
        usr.save()
        subject = 'Registration Disapproved'
        message = (
            f"Hello {usr.username},\n\n"
            f"Your registration has been disapproved by the admin."
        )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [usr.email]
        )
        messages.info(request,'User disapproved.')
    return redirect('approvalpage')



@login_required(login_url='loginpage')
def resetpage(request):
        return render(request, 'resetpage.html')


def reset_password_fun(request):
    if request.method == 'POST':
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('resetpage')
        
        if pas == cpas:
            if len(pas) < 8 or not any(char.isupper() for char in pas) \
                or not any(char.isdigit() for char in pas) \
                or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas):
                messages.error(request, 'Password must be at least 8 characters long and contain at least one uppercase letter, one digit, and one special character.')
                return redirect('resetpage')
            else:
                usr = request.user.id
                tusr = CustomUser.objects.get(id=usr)
                tusr.set_password(pas)  
                tusr.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('loginpage')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('resetpage')
    
    return render(request, 'resetpage.html')


def logoutfun(request):
    auth.logout(request)
    return redirect('loginpage')

@login_required(login_url='loginpage')
def user_list(request):
    users = CustomUser.objects.filter(status='1')
    return render(request, 'user_list.html', {'users': users})

@login_required(login_url='loginpage')
def delete_user(request, id):
    customer = get_object_or_404(CustomUser, id=id)
    if customer.image:
        if os.path.isfile(customer.image.path):
            os.remove(customer.image.path)
    customer.delete()
    messages.success(request, "User deleted successfully")
    return redirect('user_list')

@login_required(login_url='loginpage')
def profile_view(request):
    return render(request, 'profile.html')



def overdue_alerts(request):
    context = {
        'user_overdue_count': 0,
        'admin_overdue_count': 0,
        'admin_overdue_list': []
    }
    if request.user.is_authenticated:
        hidden_user_notifications = request.session.get(
            'hidden_user_notifications',
            []
        )
        context['user_overdue_count'] = Rental.objects.filter(
            user=request.user,
            status='rented',
            due_date__lt=date.today()
        ).exclude(
            id__in=hidden_user_notifications
        ).count()

        if request.user.is_staff:

            hidden_notifications = request.session.get('hidden_notifications',[])
            overdue_rentals = Rental.objects.filter(
                status='rented',
                due_date__lt=date.today()
            ).exclude(id__in=hidden_notifications).select_related(
                'user',
                'book'
            )
            context['admin_overdue_list'] = overdue_rentals
            context['admin_overdue_count'] = overdue_rentals.count()
    return context

@login_required(login_url='loginpage')
def profile_update(request):
    if request.method == 'POST':

        first_name = request.POST.get('fname').strip()
        last_name = request.POST.get('lname').strip()
        user_name = request.POST.get('uname').strip()
        email = request.POST.get('email').strip().lower()
        age = request.POST.get('age')
        phone = request.POST.get('phone').strip()
        address = request.POST.get('address').strip()
        image = request.FILES.get('image')

        if CustomUser.objects.filter(username=user_name).exclude(id=request.user.id).exists():
            messages.error(request, 'This username already exists')
            return redirect('profile_update')

        if CustomUser.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'This email is already registered')
            return redirect('profile_update')

        if not re.match(r'^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@(gmail\.com)$', email):
            messages.error(request, 'Enter a valid Gmail address (example@gmail.com)')
            return redirect('profile_update')

        if not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Phone number must be exactly 10 digits')
            return redirect('profile_update')


        if CustomUser.objects.filter(Phone_number=phone).exclude(id=request.user.id).exists():
            messages.error(request, 'Phone number already exists')
            return redirect('profile_update')

    
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.username = user_name
        request.user.email = email
        request.user.Age = age
        request.user.Phone_number = phone
        request.user.address = address
       
        if image:
            request.user.image = image

        request.user.save()

        messages.success(request, "Your profile has been updated!")
        return redirect('profile_view')

    return render(request, 'profile_update.html')


@login_required(login_url='loginpage')
def user_history(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    rentals = Rental.objects.filter(user=user).order_by('-rent_date')
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'order_history.html', {
        'user_obj': user,
        'rentals': rentals,
        'orders': orders,
    })


@login_required(login_url='loginpage')
def all_rental_history(request):
    rentals = Rental.objects.select_related(
        'user',
        'book'
    ).order_by('-rent_date')

    search = request.GET.get('search')
    status = request.GET.get('status')

    if search:
        rentals = rentals.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(book__title__icontains=search)
        )

    if status:
        rentals = rentals.filter(status=status)

    context = {
        'rentals': rentals,
        'search': search,
        'status': status,
    }

    return render(request,'all_rental_history.html',context)

@login_required(login_url='loginpage')
def all_purchase_history(request):
    order_items = OrderItem.objects.select_related(
        'order',
        'order__user',
        'book'
    ).order_by('-order__created_at')

    search = request.GET.get('search')
    if search:
        order_items = order_items.filter(
            Q(order__user__username__icontains=search) |
            Q(order__user__first_name__icontains=search) |
            Q(order__user__last_name__icontains=search) |
            Q(book__title__icontains=search)

        )
    context = {
        'order_items': order_items,
        'search': search,
    }
    return render(request,'all_purchase_history.html',context)


@login_required(login_url='loginpage')
def admin_notifications(request):
    hidden_notifications = request.session.get(
        'hidden_notifications',[])
    overdue_rentals = Rental.objects.filter(
        status='rented',
        due_date__lt=date.today()
    ).exclude(
        id__in=hidden_notifications
    ).select_related(
        'user',
        'book'
    ).order_by('due_date')
    for rental in overdue_rentals:
        rental.current_fine = rental.calculate_fine()
        rental.save()
    overdue_count = overdue_rentals.count()
    return render(
        request,
        'admin_notifications.html',
        {
            'overdue_rentals': overdue_rentals,
            'overdue_count': overdue_count
        }
    )




@login_required(login_url='loginpage')
def hide_notification(request, rental_id):

    hidden_notifications = request.session.get(
        'hidden_notifications'
    ) or []

    if rental_id not in hidden_notifications:

        hidden_notifications.append(rental_id)

    request.session[
        'hidden_notifications'
    ] = hidden_notifications

    remaining_count = Rental.objects.filter(
        status='rented',
        due_date__lt=date.today()
    ).exclude(
        id__in=hidden_notifications
    ).count()

    return JsonResponse({

        'success': True,

        'remaining_count': remaining_count

    })

@login_required(login_url='loginpage')
def user_notifications(request):
    hidden_user_notifications = request.session.get('hidden_user_notifications',[])

    overdue_rentals = Rental.objects.filter(
        user=request.user,
        status='rented',
        due_date__lt=date.today()
    ).exclude(
        id__in=hidden_user_notifications
    ).select_related(
        'book'
    ).order_by('due_date')
    for rental in overdue_rentals:
        rental.current_fine = rental.calculate_fine()
        rental.save()
    user_overdue_count = overdue_rentals.count()
    return render(request,'user_notifications.html',
        {
            'overdue_rentals': overdue_rentals,
            'user_overdue_count': user_overdue_count
        }
    )


def hide_user_notification(request, rental_id):
    hidden_user_notifications = request.session.get('hidden_user_notifications',[])
    if rental_id not in hidden_user_notifications:
        hidden_user_notifications.append(rental_id)
    request.session[
        'hidden_user_notifications'
    ] = hidden_user_notifications
    return JsonResponse({'success': True})