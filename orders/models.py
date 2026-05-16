from django.db import models
from django.conf import settings
from books.models import Book
from datetime import date

User = settings.AUTH_USER_MODEL



class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def get_grand_total(self):
        return sum(item.get_total_price()
            for item in self.items.all()
        )
    def __str__(self):
        return f"Cart - {self.user}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def get_total_price(self):
        return self.quantity * self.book.price
    def __str__(self):
        return f"{self.book.title} x {self.quantity}"



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order #{self.id}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    def __str__(self):
        return f"{self.book.title} - {self.quantity}"



class Rental(models.Model):
    STATUS_CHOICES = [
        ('rented', 'Rented'),

        ('returned', 'Returned'),

        ('lost', 'Lost'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    rent_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True,null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rented'
    )

    current_fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    rent_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00
    )

    is_fine_paid = models.BooleanField(default=False)  

    def calculate_fine(self):      
        if self.status == 'lost':
            return self.book.price + 100
        today = date.today()        
        if self.return_date:
            check_date = self.return_date        
        else:
            check_date = today        
        late_days = (check_date - self.due_date).days        
        if late_days > 0:
            return late_days * 10
        return 0

    def save(self, *args, **kwargs):
        self.current_fine = self.calculate_fine()
        super().save(*args, **kwargs)


    def mark_as_lost(self):
        self.status = 'lost'
        self.return_date = date.today()
        self.current_fine = (self.book.price + 100)
        self.save(
            update_fields=[
                'status',
                'return_date',
                'current_fine'
            ]
        )
    def __str__(self):
        return f"{self.book.title} - {self.user}"