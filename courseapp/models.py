from django.db import models
from django.conf import settings
import os
from django import forms
from django.forms import ModelForm
from trainers.models import Trainer
from topicapp.models import Topic
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator 

# Create your models here.

def get_image_choices():
        # Define the directory where images are stored
        image_folder = os.path.join(settings.MEDIA_ROOT, 'images')
        image_files = []

        # Get a list of image files from the folder
        if os.path.exists(image_folder):
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    # Store the filename as a tuple (file, file)
                    image_files.append((f'images/{filename}', filename))
        return image_files

class Course(models.Model):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField(max_length=1000)
    topic = models.ManyToManyField(Topic, blank=False)
    duration = models.PositiveIntegerField(verbose_name='Duration (days)', default=0, validators=[MinValueValidator(30), MaxValueValidator(200)])
    trainers = models.ManyToManyField(Trainer, verbose_name="Trainers")
    fees = models.PositiveIntegerField(verbose_name="Course Fee (Rs.)", validators=[MinValueValidator(5000), MaxValueValidator(80000)])
    uploaded_file = models.FileField(verbose_name='Course Content', upload_to='documents/')
    image = models.CharField(max_length=255, choices=get_image_choices())
    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_update', kwargs={'pk': self.pk})


class CourseForm(ModelForm):
    class Meta:
        uploaded_file = forms.FileField(
        required=False,
         label='Course Content'
        )
        
        model = Course
        fields = '__all__'
        exclude = ['status']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the 'topics' field with active topics
        self.fields['topic'].queryset = Topic.objects.filter(status=True)
        self.fields['trainers'].queryset = Trainer.objects.filter(status=True)
        # print(Trainer.objects.filter(status=True))
