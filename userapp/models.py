from django.db import models
from django.conf import settings
from batchapp.models import Batch
from django.contrib.auth.models import User, AbstractUser

from courseapp.models import Course
from trainers.models import Trainer


class UserProfile(models.Model):
    QUALIFICATION_CHOICES = [
        ('Secondary Schooler', 'School/10th/below 10th class'),
        ('High Schooler', 'High School/Intermediate'),
        ('BCA', 'BCA'),
        ('B.E', 'B.E'),
        ('B.Sc', 'B.Sc'),
        ('B.Tech', 'B.Tech'),
        ('MBA', 'MBA'),
        ('MCA', 'MCA'),
        ('M.E', 'M.E'),
        ('M.Sc', 'M.Sc'),
        ('M.Tech', 'M.Tech'),
        ('Other', 'Any Other Qualification'),
    ]

    POSITION_CHOICES = [
        ('', ''),
        ('Student', 'Student'),
        ('IT Job Aspirant', 'IT Job Aspirant'),
        ('Non IT Professional', 'Non IT Professional'),
        ('IT Professional', 'IT Professional'),
    ]


    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Dynamically refer to the custom user model
        on_delete=models.CASCADE
    )
    country_code = models.CharField(max_length=3, default="091")
    mobile_number = models.CharField(max_length=15, default="")
    qualification = models.CharField(max_length=30, choices=QUALIFICATION_CHOICES)
    # Add any other fields you need for the profile
    city = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=30, default="")
    position = models.CharField(max_length=30, default="", choices=POSITION_CHOICES)
    photo = models.ImageField(verbose_name='Photo', default="", upload_to='user_photos/')

    def __str__(self):
        return f"{self.user.email}"

class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Make email the primary identifier

    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = ['first_name', 'last_name']

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.IntegerField(unique=True)
    message = models.TextField()

    def __str__(self):
        return self.name
    

class Enrollment(models.Model):

    ENROLLMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('deactivated', 'Auto Cancelled'),
        ('reserved', 'Seat Reserved'),
        ('confirmed', 'Seat Confirmed'),
        ('closed', 'Closed'),
    ]

    #first_name = models.CharField(max_length=50)
    #last_name = models.CharField(max_length=50)
    #email = models.EmailField(max_length=50)
    #mobile_number = models.CharField(max_length=15)
    #user = models.ManyToManyField(UserProfile)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    #course_title = models.CharField(max_length=100)
    adv_status = models.BooleanField(default=False)
    full_status = models.BooleanField(default=False)
    adv_fee = models.DecimalField(max_digits=5, default=500, decimal_places=2, null=True, blank=True)
    course_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    adv_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    full_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    enrollment_status = models.CharField(max_length=50, choices=ENROLLMENT_STATUS_CHOICES, default='pending')
    all_links_accessible = models.BooleanField(default=False)
    enrollment_date = models.DateTimeField(auto_now_add=True)  # Set when student data is created
    reservation_last_date = models.DateTimeField(null=True, blank=True)
    adv_payment_date = models.DateTimeField(null=True, blank=True)  # Set when adv payment is made
    confirmation_last_date = models.DateTimeField(null=True, blank=True)
    full_payment_date = models.DateTimeField(null=True, blank=True)  # Set when full payment is made
    #course_start_date = models.DateField(null=True, blank=True)
    #course_duration = models.PositiveIntegerField(default=0)
    #class_start_time = models.TimeField(null=True, blank=True)
    #class_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):  
        return f"{self.user.id}: {self.user.mobile_number} - {self.batch.course.title}"


class Story(models.Model):
    course = models.ForeignKey(Batch, on_delete=models.CASCADE,null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE,null=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True)

    comments = models.CharField(max_length=1000)  # 200 words validation needed
    rating = models.FloatField(choices=[
        (1, 1), (1.5, 1.5), (2, 2), (2.5, 2.5),
        (3, 3), (3.5, 3.5), (4, 4), (4.5, 4.5), (5, 5)
    ])
    status = models.CharField(max_length=20, choices=[
        ('Created', 'Created'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    date = models.DateTimeField(auto_now_add=True)

class CourseFeedback(models.Model):
    STATUS_CHOICES = [
        ('Created', 'Created'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Created')  # <-- Added this line

    def __str__(self):
        return f"{self.trainer} feedback on {self.course}"