from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=8,decimal_places=2)
    description = models.CharField(max_length=255)
    cover_image = models.FileField(upload_to='image/',null=True)

    stock = models.PositiveIntegerField(default=0)
    available_stock = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.available_stock > self.stock:
            self.available_stock = self.stock
        super().save(*args, **kwargs)




