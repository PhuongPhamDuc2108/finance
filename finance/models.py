from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django import forms

class Income(models.Model):
    SOURCE_CHOICES = [
        ('Salary', 'Lương'),
        ('Business', 'Kinh doanh'),
        ('Investment', 'Đầu tư'),
        ('Other', 'Khác'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, default='Other')
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.source} - {self.amount}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Thực phẩm'),
        ('Education', 'Giáo dục'),
        ('Entertainment', 'Giải trí'),
        ('Transport', 'Di chuyển'),
        ('Other', 'Khác'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Other')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.category} - {self.amount}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='img/profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    



