from django import forms
from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from .models import Enrollment
from userapp.models import CustomUser
from .models import UserProfile
from django.contrib.auth import authenticate
import re
import requests

def verify_recaptcha(recaptcha_response):
    secret_key = settings.RECAPTCHA_PRIVATE_KEY
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    response = requests.post(verify_url, data=data)
    result = response.json()
    return result.get('success', False)

class AdminRegistrationForm(UserCreationForm):
    captcha = ReCaptchaField(
        required=True,
        label="Captcha *"
    )

    first_name = forms.CharField(
        required=True,
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )

    last_name = forms.CharField(
        required=True,
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )

    email = forms.EmailField(
        required=True,
        max_length=60,
        label="Email",
        error_messages={
            'required': 'Email is mandatory.',
            'invalid': 'Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.',
        },
        help_text="This will be your username for the account and provide access to administrative features."
    )

    mobile_number = forms.CharField(
        required=True,
        max_length=10,
        label="Mobile Number",
        help_text="Mobile number will be used for important updates about the system."
    )

    password1 = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
        help_text=(
            '<ul>'
            '<li>Your password must contain at least 8 characters.</li>'
            '<li>Your password can’t be a commonly used password.</li>'
            '<li>Your password can’t be entirely numeric.</li>'
            '</ul>'
        ),
    )

    password2 = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Re-enter your password"}),
        help_text="Re-enter the same password as above for verification.",
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'password1', 'password2', 'captcha']

        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        # Extract the 'request' argument from kwargs, if present
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if 'password1' in self.errors:
            # Focus on password1 if it has an error
            self.fields['password1'].widget.attrs['autofocus'] = 'autofocus'
        elif 'password2' in self.errors:
            # Focus on password2 if it has an error
            self.fields['password2'].widget.attrs['autofocus'] = 'autofocus'

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email is already in use
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")

        # Check if the email ends with '@gmail.com'
        if email and not email.endswith('@gmail.com'):
            raise ValidationError('Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.')

        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')

        # Check if mobile number is numeric and 10 digits long
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits.")

        return mobile_number

    def save(self, commit=True):
        # Save the user instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Save the mobile number to the UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.mobile_number = self.cleaned_data['mobile_number']
            profile.save()

        return user

class AdminProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )

    last_name = forms.CharField(
        required=True,
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )

    email = forms.EmailField(
        required=True,
        max_length=60,
        label="Email",
        help_text="Your Gmail ID is not editable. This will be used as your username for the system.",
        error_messages={
            'required': 'Email is mandatory.',
            'invalid': 'Only valid Gmail IDs are accepted. Please enter your Gmail ID.'
        }
    )

    mobile_number = forms.CharField(
        required=True,
        max_length=10,
        label="Mobile Number",
        help_text="Your mobile number will be used for important system updates."
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password (optional)"}),
        help_text="Enter a new password only if you wish to change it."
    )

    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        help_text="Re-enter the password to confirm."
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'password', 'password_confirm']
    
    def __init__(self, *args, **kwargs):
        # Extract 'request' if passed
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Autofocus on password fields if there are errors
        if 'password' in self.errors:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
        elif 'password_confirm' in self.errors:
            self.fields['password_confirm'].widget.attrs['autofocus'] = 'autofocus'

    def clean_username(self):
        # Ensure that the username is not taken by another user
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def clean_mobile_number(self):
        # Validate mobile number
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobile_number) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # If a new password is provided, ensure it matches the confirmation
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match.")
            # Optional: Validate password strength
            if password:
                validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:  # Only update the password if it's not empty
            user.set_password(password)  # Hash and set the password
        else:
            # Ensure the password remains unchanged by fetching it directly from the database
            user.password = CustomUser.objects.get(pk=user.pk).password

        if commit:
            user.save()

            # Update the UserProfile with the mobile number
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.mobile_number = self.cleaned_data['mobile_number']
            profile.save()

        return user
    
class StudentRegistrationForm(UserCreationForm):
    QUALIFICATION_CHOICES = [
        ('', ''),
        ('Secondary Schooler', '10th / below 10th class'),
        ('High Schooler', '12th class / Intermediate'),
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

    captcha = ReCaptchaField(
        required=True,
        label="Captcha *"
    )

    first_name = forms.CharField(
        required=True,
        max_length=30,
        label="First Name *",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )

    last_name = forms.CharField(
        required=True,
        max_length=30,
        label="Last Name *",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )

    email = forms.EmailField(
        required=True,
        max_length=60,
        label="Email *",
        error_messages={
            'required': 'Email is mandatory.',
            'invalid': 'Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.',
        },
        help_text="This will be your username of your account and also provide access to entire course material in Google Drive during the course."
    )
    
    country_code = forms.CharField(
        required=True,
        max_length=3,
        label="Country Code *",
        widget=forms.TextInput(attrs={"placeholder": "Ex: 091"}),
        help_text="<br /><br />"
    )

    mobile_number = forms.CharField(
        required=True,
        max_length=10,
        label="Mobile Number *",
        help_text="Should be a 10-digit Mobile number (No '+' required) and will be used to give you updates about the registered course over your WhatsApp."
    )

    qualification = forms.ChoiceField(
        required=True,
        label="Qualification*",
        choices=QUALIFICATION_CHOICES,
    )

    city = forms.CharField(
        required=True,
        max_length=30,
        label="City *"
    )

    country = forms.CharField(
        required=True,
        max_length=30,
        label="Country *"
    )

    position = forms.ChoiceField(
        required=True,
        label="You are*",
        choices=POSITION_CHOICES,
    )

    password1 = forms.CharField(
        required=True,
        label="Password *",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
        help_text=(
            '<ul>'
            '<li>Your password must contain at least 8 characters.</li>'
            '<li>Your password can’t be a commonly used password.</li>'
            '<li>Your password can’t be entirely numeric.</li>'
            '</ul>'
        ),
    )

    password2 = forms.CharField(
        required=True,
        label="Confirm Password *",
        widget=forms.PasswordInput(attrs={"placeholder": "Re-enter your password"}),
        help_text="Re-enter the same password as above for verification.",
    )

    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ['first_name', 'last_name', 'email', 'country_code', 'mobile_number', 'qualification', 'position', 'city', 'country', 'password1', 'password2', 'captcha']

        widgets = {
            'password': forms.PasswordInput(),
            'country_code': forms.TextInput(),
        }

    # def __init__(self, *args, **kwargs):
    #     # Extract the 'request' argument from kwargs, if present
    #     self.request = kwargs.pop('request', None)
    #     super().__init__(*args, **kwargs)

    #     if 'password1' in self.errors:
    #         # Focus on password1 if it has an error
    #         self.fields['password1'].widget.attrs['autofocus'] = 'autofocus'
    #     elif 'password2' in self.errors:
    #         # Focus on password2 if it has an error
    #         self.fields['password2'].widget.attrs['autofocus'] = 'autofocus'

    # =========== JCWT 1 - Confirm pass focus
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super().__init__(*args, **kwargs)

    #     # Remove autofocus from all fields initially
    #     for field in self.fields.values():
    #         field.widget.attrs.pop('autofocus', None)

    #     # Set autofocus on the first field with an error
    #     for field_name in self.errors:
    #         if field_name in self.fields:
    #             self.fields[field_name].widget.attrs['autofocus'] = 'autofocus'
    #             break

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Remove autofocus from all fields initially
        for field in self.fields.values():
            field.widget.attrs.pop('autofocus', None)

        # Always prioritize autofocus for 'password1' if it has errors
        if 'password1' in self.errors:
            self.fields['password1'].widget.attrs['autofocus'] = 'autofocus'
        else:
            # Set autofocus on the first other field with an error
            for field_name in self.errors:
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs['autofocus'] = 'autofocus'
                    break

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email is already in use in CustomUser model
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")

        # Check if the email ends with '@gmail.com'
        if email and not email.endswith('@gmail.com'):
            raise ValidationError('Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.')

        return email

    def save(self, commit=True):
        # Save user instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Save the mobile number to the UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.mobile_number = self.cleaned_data['mobile_number']
            profile.qualification = self.cleaned_data['qualification']
            profile.position = self.cleaned_data['position']
            profile.city = self.cleaned_data['city']
            profile.country = self.cleaned_data['country']
            profile.photo = r"user_photos/UnknownUser.jpg"
            profile.save()
            user.profile = profile
        return user


class UserProfileEditForm(forms.ModelForm):
    QUALIFICATION_CHOICES = [
        ('', ''),
        ('Secondary Schooler', '10th / below 10th class'),
        ('High Schooler', '12th class / Intermediate'),
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


    first_name = forms.CharField(
        required=True,
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )

    last_name = forms.CharField(
        required=True,
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )

    email = forms.CharField(
            label="Email",
            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            help_text="This email id is nothing but your username and can't be modified."
            )

    # email = forms.EmailField(
    #     required=True,
    #     max_length=60,    #     label="Email *",
    #     error_messages={
    #         'required': 'Email is mandatory.',
    #         'invalid': 'Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.',
    #     },
    #     help_text="This will be your username of your account and also provide access to entire course material in Google Drive during the course."
    # )

    mobile_number = forms.CharField(
        required=True,
        max_length=12,
        label="Mobile Number",
        help_text="Mobile number will be used to give you updates about the registered course over your WhatsApp."
    )

    qualification = forms.ChoiceField(
        required=True,
        label="Qualification",
        choices=QUALIFICATION_CHOICES,
    )

    city = forms.CharField(
        required=True,
        max_length=30,
        label="City",
        error_messages={
            'required': 'City is mandatory.'
        }
    )

    country = forms.CharField(
        required=True,
        max_length=30,
        label="Country",
        error_messages={
            'required': 'Country is mandatory.'
        }
    )

    position = forms.ChoiceField(
        required=True,
        label="Designation",
        choices=POSITION_CHOICES
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password (optional)"}),
        help_text="Enter a new password only if you wish to change it."
    )

    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        help_text="Re-enter the password to confirm."
    )

    photo = forms.ImageField(
        required=False,
        help_text="Upload profile picture here."
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'qualification', 'position', 'city', 'country', 'photo', 'password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        # Extract 'request' if passed
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Autofocus on password fields if there are errors
        if 'password' in self.errors:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
        elif 'password_confirm' in self.errors:
            self.fields['password_confirm'].widget.attrs['autofocus'] = 'autofocus'

    def clean_username(self):
        # Ensure that the username is not taken by another user
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def clean_mobile_number(self):
        # Validate mobile number
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobile_number) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile_number

    def clean_qualification(self):
        # Validate qualification
        qualification = self.cleaned_data.get('qualification')
        if qualification == '':
            raise forms.ValidationError("Please select Qualification.")
        return qualification

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # If a new password is provided, ensure it matches the confirmation
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match.")
            # Optional: Validate password strength
            if password:
                validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:  # Only update the password if it's not empty
            user.set_password(password)  # Hash and set the password
        else:
            # Ensure the password remains unchanged by fetching it directly from the database
            user.password = CustomUser.objects.get(pk=user.pk).password

        if commit:
            user.save()

            # Update the UserProfile with the mobile number
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.mobile_number = self.cleaned_data['mobile_number']
            profile.qualification = self.cleaned_data['qualification']
            profile.position = self.cleaned_data['position']
            profile.city = self.cleaned_data['city']
            profile.country = self.cleaned_data['country']
            profile.photo = self.cleaned_data['photo']
            profile.save()

        return user


class CustomLoginForm(AuthenticationForm):
    captcha = ReCaptchaField()  # Add the captcha field

    class Meta:
        fields = ['username', 'password', 'captcha']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get("request", None)
        if self.request is None:
            raise ValueError("Request is required for this form")
        super().__init__(*args, **kwargs)

    # def clean(self):
    #     email = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')

    #     if email and password:
    #         # Check if the email exists in the database
    #         try:
    #             user = CustomUser.objects.get(email=email)
    #         except CustomUser.DoesNotExist:
    #             raise ValidationError("Email not found. Please enter a valid email.")

    #         # Authenticate the user
    #         user = authenticate(username=email, password=password)
    #         if user is None:
    #             raise ValidationError("Incorrect password. Please try again.")

    #         # Check if the user is active
    #         if not user.is_active:
    #             raise ValidationError("Your account is inactive. Please contact support.")

    #     return self.cleaned_data

    def clean(self):
        # Fetch the data from the form fields
        email = self.cleaned_data.get('username')  # 'username' is used as the email
        password = self.cleaned_data.get('password')

        # Custom validation for email and password
        if email and password:
            # Check if the user exists in the database
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise ValidationError("Email not found. Please enter a valid email.")

            # Authenticate the user
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password. Please try again.")

            # Check if the user is active
            if not user.is_active:
                raise ValidationError("Your account is inactive. Please contact support.")
        else:
            raise ValidationError("Both email and password are required.")

        # Optionally return the cleaned data (no need to call super().clean())
        return self.cleaned_data
    
    def get_user(self):
        return authenticate(
            self.request, 
            username=self.cleaned_data.get('username'), 
            password=self.cleaned_data.get('password')
        )

# class CourseRegistrationForm(forms.ModelForm):
#     captcha = ReCaptchaField()
#     email = forms.EmailField(
#         max_length=60,
#         error_messages={
#             'required': 'Email is mandatory.',
#             'invalid': 'Only valid Gmail IDs are accepted for registration. Please enter your Gmail ID.',
#         },
#         help_text="This will be your username of your account and also provided access to entire course material in Google Drive during the course."
#     )
#     # mobile_number = forms.CharField(
#     #     max_length=10,
#     #     help_text="Mobile number will be used to give you updates about registered course over your WhatsApp."
#     # )
#     # select_batch = forms.ModelChoiceField(
#     #     queryset=Batch.objects.filter(status=True),  # Get only open batches
#     #     label='Batch No',
#     #     empty_label='Select a Batch',  # Placeholder for dropdown
#     #     error_messages={'required': 'This field is mandatory.'}
#     # )
#
#     class Meta:
#         model = Enrollment
#         fields = ['first_name', 'last_name', 'email', 'captcha']
#
#     def __init__(self, *args, **kwargs):
#         course_title = kwargs.pop('course_title', None)
#         self.request = kwargs.pop('request', None)
#         if self.request is None:
#             raise ValueError("Request is required for this form")
#         super(CourseRegistrationForm, self).__init__(*args, **kwargs)
#
#         # if course_title:
#         #     # Filter the select_batch field to show only batches linked to the specific course
#         #     self.fields['select_batch'].queryset = Batch.objects.filter(course__title=course_title, status="open")
#         # else:
#         #     # If no course title is provided, show an empty queryset
#         #     self.fields['select_batch'].queryset = Batch.objects.none()
#
#     def clean(self):
#         cleaned_data = super().clean()
#         # recaptcha_response = self.request.POST.get('g-recaptcha-response')
#         # # Call the verify_recaptcha function to validate the captcha
#         # if recaptcha_response:
#         #     is_recaptcha_valid = verify_recaptcha(recaptcha_response)
#         #     if not is_recaptcha_valid:
#         #         raise ValidationError('Invalid ReCaptcha. Please try again.')
#         # else:
#         #     raise ValidationError('ReCaptcha is required. Please complete the ReCaptcha.')
#
#         return cleaned_data

class PaymentForm(forms.Form):
    pass
