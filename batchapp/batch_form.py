from django import forms
from django.core.exceptions import ValidationError
from .models import Batch
from shared.constants import DAYS_OF_WEEK
from courseapp.models import Course

class BatchForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    class Meta:
        model = Batch
        fields = '__all__'  # We'll exclude fields dynamically

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
        exclude = ['end_date']  # Always exclude end_date

    def clean_days(self):
        """
        Convert the list of selected days back to a comma-separated string.
        """
        selected_days = self.cleaned_data.get('days', [])
        return ','.join(selected_days)

    def __init__(self, *args, **kwargs):
        # Determine if it's an add or edit form by checking if an instance is passed
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if not instance or not instance.pk:
            # This is an Add form (no instance exists), so pre-select all days by default
            self.fields['days'].initial = [day[0] for day in DAYS_OF_WEEK if day[-1] != 'Sunday' ]
        else:
            # This is an Edit form (instance exists)
            # Pre-populate the checkboxes with selected days
            if instance.days:
                self.fields['days'].initial = instance.days.split(',')

        # Customize queryset for courses
        self.fields['course'].queryset = Course.objects.filter(status=True)

        # Dynamically exclude status field for Add forms (no instance yet)
        if not instance or not instance.pk:
            self.fields.pop('status')
            self.fields.pop('duration')
            self.fields.pop('trainers')
            self.fields.pop('fees')
            self.fields.pop('class_room_link')
            self.fields.pop('course_material_link')
            self.fields.pop('quiz_link')


