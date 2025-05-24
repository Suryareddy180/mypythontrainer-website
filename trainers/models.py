from datetime import date

from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from shared.constants import COUNTRY_CODES

def validate_gmail(email):
    if not email.endswith('@gmail.com'):
        raise ValidationError("Email must be a Gmail address.")

# Create your models here.

class Trainer(models.Model):
    name = models.CharField(max_length=50, verbose_name="Full Name")
    title = models.CharField(max_length=100, verbose_name="Professional Title / Specialization", null=True, blank=True)  # Made nullable
    bio = models.TextField(
        verbose_name="Trainer Bio",
        help_text="Provide a detailed biography.",
        default="This is a placeholder bio."
    )
    dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)  # Made nullable

    training_exp = models.PositiveIntegerField(verbose_name="Training Experience (Years)", validators=[MinValueValidator(0), MaxValueValidator(50)])
    prior_batches = models.PositiveIntegerField(default=0, verbose_name="Prior Batches")
    prior_aspirants = models.PositiveIntegerField(default=0, verbose_name="Prior Aspirants")
    prior_weekly_tests = models.PositiveIntegerField(default=0, verbose_name="Prior Weekly Tests")

    rating = models.DecimalField(
        verbose_name="Rating (1-5)",
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )

    email = models.EmailField(
        max_length=60,
        validators=[validate_gmail],
        help_text="Official communication email (Gmail only)."
    )
    country_code = models.CharField(max_length=3, choices=COUNTRY_CODES, default='+91')
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Mobile number must be exactly 10 digits.')],
        help_text='Used for WhatsApp communication.'
    )

    picture = models.ImageField(upload_to='trainer_profiles/', verbose_name="Profile Picture",null=True,default=None)

    qualifications = models.ManyToManyField('Qualification', verbose_name="Qualifications")
    organizations = models.ManyToManyField('Organization', verbose_name="IT Experience")
    awards = models.ManyToManyField('Award', blank=True, verbose_name="Trainer Awards")
    status = models.BooleanField(default=True, verbose_name="Active Status")

    def __str__(self):
        return f"Shri. {self.name} ({self.title})"

    def get_absolute_url(self):
        return reverse('trainer_one', kwargs={'pk': self.pk})

    @property
    def age(self):
        return date.today().year - self.dob.year if self.dob else None

    @property
    def total_it_experience(self):
        return sum(
            (org.to_year if org.to_year != 0 else date.today().year) - org.from_year
            for org in self.organizations.all()
        )

class Degree(models.Model):
    title = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    certificate = models.FileField(upload_to='certificates/')

    def __str__(self):
        return self.title


class College(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    short_name = models.CharField(max_length=50, verbose_name="Short Name")
    city = models.CharField(max_length=100, verbose_name="City")
    country = models.CharField(max_length=100, verbose_name="Country")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Status")

    def __str__(self):
        return f"{self.short_name} - {self.city}"


class Qualification(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.degree.short_name} "


class Organization(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    from_year = models.PositiveIntegerField(verbose_name="From Year")
    to_year = models.PositiveIntegerField(verbose_name="To Year", help_text="Enter 0 if currently working")
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    short_name = models.CharField(max_length=100, verbose_name="Short Name")
    logo = models.ImageField(upload_to='organization_logos/', verbose_name="Organization Logo")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active', verbose_name="Status")

    def __str__(self):
        return f"{self.short_name} ({self.from_year} - {self.to_year if self.to_year != 0 else 'Present'})"


class Award(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    full_title = models.CharField(max_length=255, verbose_name="Full Title")
    short_title = models.CharField(max_length=100, verbose_name="Short Title")
    certificate = models.ImageField(upload_to='award_certificates/', verbose_name="Certificate Image")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active', verbose_name="Status")

    def __str__(self):
        return self.short_title
