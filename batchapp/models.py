from django.db import models
from courseapp.models import Course
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from trainers.models import Trainer

class Batch(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('open', 'Registrations Open'),
        ('freezed', 'Freezed'),
        ('completed', 'Completed'),
    ]

    LANGUAGE_CHOICES = [
        ('', ''),
        ('Telugu', 'Telugu'),
        ('English', 'English')
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    tentative = models.BooleanField(default=False)
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    days = models.CharField(verbose_name='Days', max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    end_date = models.DateField(blank=True, null=True)

    duration = models.PositiveIntegerField(verbose_name='Duration (days)', default=0, validators=[MinValueValidator(30), MaxValueValidator(200)])
    trainers = models.ManyToManyField(Trainer, verbose_name="Trainers")
    fees = models.PositiveIntegerField(verbose_name="Course Fee (Rs.)", default=0, validators=[MinValueValidator(5000), MaxValueValidator(80000)])

    dummy_registrations = models.PositiveIntegerField(verbose_name="Dummy Registrations", default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    language = models.CharField(verbose_name="Language", max_length=15, choices=LANGUAGE_CHOICES, default="")
    youtube_link = models.URLField(verbose_name='Demo Link', blank=True, null=True)
    class_room_link = models.URLField(verbose_name='Online Classroom Link', blank=True, null=True)
    course_material_link = models.URLField(verbose_name='Material Link', blank=True, null=True)
    quiz_link = models.URLField(verbose_name='Weekly Test Link', blank=True, null=True)
    poc_name = models.CharField(verbose_name='Admin Name', max_length=50, blank=True)
    poc_mobile_no = models.CharField(verbose_name='Admin Mobile Number', max_length=10, validators=[RegexValidator(r'^\d{10}$', 'Mobile number must be exactly 10 digits.')], help_text='This is Batch Admin Mobile number and will be shared to entire batch students.', blank=True)


    def save(self, *args, **kwargs):
        if self.start_date and self.course:
            self.end_date = self.start_date + relativedelta(days=self.course.duration)
            self.end_date += timedelta(days=10)

        if self.course:
            self.duration = self.duration if self.duration else self.course.duration
            self.fees = self.fees if self.fees else self.course.fees
        super(Batch, self).save(*args, **kwargs)
        self.trainers.set(self.course.trainers.all())


    def __str__(self):
        return self.batch_number

    @property
    def get_start_end_dates(self):
        """Return formatted Start – End Dates as '<Start Date> to <End Date>'"""
        if self.start_date and self.end_date:
            formatted_start_date = self.start_date.strftime("%b %d, %Y")
            formatted_end_date = self.end_date.strftime("%b %d, %Y")
            return f'{formatted_start_date} to {formatted_end_date}'
        return 'Dates not available'