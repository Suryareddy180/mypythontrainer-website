from django.db import models
from courseapp.models import Course
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from shared.constants import COUNTRY_CODES

# Create your models here.

def validate_gmail(email):
    if not email.endswith('@gmail.com'):
        raise ValidationError("Email must be a Gmail address.")
    if Student.objects.filter(email=email).exists():
        raise ValidationError("This email is already registered.")


class Student(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email_id = models.EmailField(max_length=60, 
                                 unique=True,
                                 help_text="This will be your username of your account and also provided access to entire course material in Google Drive during the course.")
    country_code = models.CharField(max_length=3, choices=COUNTRY_CODES, default='+91')
    
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Mobile number must be exactly 10 digits.')],
        help_text='Mobile number will be used to give you updates about registered course over your WhatsApp.',
    )
    select_batch = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.first_name + self.last_name
