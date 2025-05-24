from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.forms import ModelForm
from .models import Contact
from courseapp.models import Course
from django.contrib.auth import login, update_session_auth_hash
from django.views.generic import View, CreateView, TemplateView, ListView, DetailView, UpdateView
from django.views.generic.edit import FormView
#from .forms import AdminRegistrationForm, StudentRegistrationForm, UserProfileEditForm, CustomLoginForm, CourseRegistrationForm, PaymentForm
from .forms import AdminRegistrationForm, StudentRegistrationForm, UserProfileEditForm, CustomLoginForm, PaymentForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from .models import Enrollment, Batch
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Case, When, BooleanField
from userapp.models import UserProfile
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from trainers.models import Trainer

# Create your views here.
class RegisterAdminView(CreateView):
    form_class = AdminRegistrationForm
    template_name = 'adminapp/register.html'
    success_url = reverse_lazy('userapp:login')

    def get_form_kwargs(self):
        # Call the parent class to get the standard form kwargs
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.save()
        admin_group = Group.objects.get(name='Admin')
        user.groups.add(admin_group)
        # login(self.request, user)  # Automatically log in the user
        return redirect(self.success_url)
    
class RegisterStudentView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'userapp/register.html'
    success_url = reverse_lazy('userapp:login')

    def form_valid(self, form):
        user = form.save()
        student_group = Group.objects.get(name='Student')
        user.groups.add(student_group)
        # login(self.request, user)  # Automatically log in the user
        return redirect(self.success_url)
    
# class CustomLoginView(auth_views.LoginView):
#     template_name = 'userapp/login.html'
#     form_class = CustomLoginForm  # Use the custom form with captcha

#     def get_success_url(self):
#         user = self.request.user
        
#         if user.groups.filter(name='Admin').exists():
#             return reverse('adminapp:admin_home')  # Redirect Admin users to admin dashboard
#         elif user.groups.filter(name='Student').exists():
#             return reverse('userapp:home')  # Redirect Student users to student dashboard
#         return reverse('userapp:home')

# class HomeView(TemplateView):
#     template_name = 'userapp/index.html'

# class AboutPageView(TemplateView):
#     template_name = 'userapp/about.html'

# class IndexPageView(TemplateView):
#     template_name = 'userapp/index.html'

class NewIndexPageView(TemplateView):
    template_name = 'userapp/new-index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all available courses where status is active
        courses = Course.objects.filter(status=True).order_by('title')

        # Annotate each course with trainer and batch details, if available
        for course in courses:
            # Fetch all trainers linked to the course
            trainers = course.trainers.all()
            
            if trainers.exists():  # Check if there are trainers associated
                course.trainer_info = []
                for trainer in trainers:
                    trainer_info = {
                        'name': trainer.name,
                        'rating': float(trainer.rating) if trainer.rating else 0.0
                    }
                    course.trainer_info.append(trainer_info)  # Append trainer details to course.trainer_info
            else:
                course.trainer_info = None  # Handle the case where no trainers are associated

            # Fetch the first active batch linked to the course
            course.batch_info = Batch.objects.filter(course=course, status=True).first()


        # Add all the courses to the context, regardless of batch availability
        context['courses'] = courses
        return context


# class NewAboutPageView(TemplateView):
#     template_name = 'userapp/trainers.html'

class NewAboutPageView(ListView):
    template_name = "userapp/trainers.html"
    model = Trainer
    context_object_name = "tnr"

class NewRegistrationPageView(CreateView):
    template_name = 'userapp/new-registration.html'
    form_class = StudentRegistrationForm
    # template_name = 'userapp/register.html'
    success_url = reverse_lazy('userapp:login')

    def get_form_kwargs(self):
        # Call the parent class to get the standard form kwargs
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.save()
        student_group = Group.objects.get(name='Student')
        user.groups.add(student_group)

        # Render HTML template
        courses_url = r'www.mypythontrainer.com/course-calendar/'
        subject = 'Welcome to My Python Trainer!'
        html_message = render_to_string('userapp/registration_email.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mobile_number': user.profile.mobile_number,
            'all_courses': courses_url
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(
            subject,
            '',  # Leave plain-text body empty for an HTML-only email
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False
        )

        messages.success(self.request, 'Registration successful. Please login now.')
        return redirect(self.success_url)


class NewLoginPageView(auth_views.LoginView):
    template_name = 'userapp/login.html'
    form_class = CustomLoginForm

    def get_form_kwargs(self):
        # Call the parent class to get the standard form kwargs
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        
        user = self.request.user
        
        if user.groups.filter(name='Admin').exists():
            return reverse('adminapp:admin_home')  # Redirect Admin users to admin dashboard
        elif user.groups.filter(name='Student').exists():
            # Check if the user is registered in the Enrollment table
            is_registered = Enrollment.objects.filter(user__user__email=user.email).exists()
            
            if is_registered:
                # Redirect to the applied courses page if the user is registered
                return reverse('userapp:applied_courses')  # Redirect to my enrolled courses
            else:
                # Redirect to the course view page if the user is not registered
                return reverse('userapp:new_courses_calendar_page')  # Redirect to courses page
        return reverse('userapp:new_index_page')
    

class EnrollCourse(View):
    def post(self, request, course_title, batch_name):
        if not request.user.is_authenticated:
            return redirect('userapp:login')
        send_enrollment_email(self, course_title, batch_name, request.user)
        # messages.success(request, f"You have successfully enrolled in {course_title}.")
        return redirect('userapp:applied_courses')


@method_decorator(login_required, name='dispatch')
class ConfirmEnrollCourse(View):
    def post(self, request, *args, **kwargs):
        course_title = self.kwargs['course_title']
        batch_name = self.kwargs['batch_name']
        existing_enrollment = Enrollment.objects.filter(user__user__email=request.user.email, batch__course__title=course_title).first()
        if existing_enrollment:
            context = {
                'course_title': course_title,
                'batch_name': batch_name,
                'is_registered': True if existing_enrollment else False,
                'registered_batch_number': existing_enrollment.batch.batch_number if existing_enrollment else None,
                'registered_course_name': existing_enrollment.batch.course.title if existing_enrollment else None,
                'registered_batch_status': existing_enrollment.batch.status if existing_enrollment else None,
                'batch_number': batch_name
            }
            return render(request, 'userapp/enrollment_confirmation.html', context)
        else:
            send_enrollment_email(self, course_title, batch_name, request.user)

            # registered_batch = Enrollment.objects.filter(user__user__email=email, batch__course__title=self.course.title).first()
            #
            # # Check if the user is already registered and if the batch is active
            # if registered_batch:
            #     if registered_batch.batch_name.status != 'freezed':
            #         messages.error(request, "You are already enrolled in an active batch. Cannot register in a new batch.")
            #         return redirect('userapp:applied_courses')

            return redirect('userapp:applied_courses')



def send_enrollment_email(self, course_title, batch_name, user):
    batch = get_object_or_404(Batch, batch_number=batch_name)
    user_profile = get_object_or_404(UserProfile, user=user)  # UserProfile.objects.get_or_create(user=self.request.user)  # Create UserProfile if it doesn't exist
    email = user.email

    # Proceed with the registration
    today = date.today()
    if today >= batch.start_date:
        reservation_last_date = datetime.now() + timedelta(days=2)
        confirmation_last_date = datetime.now() + timedelta(days=10)
    else:
        if batch.start_date > today + timedelta(days=7):
            reservation_last_date = datetime.now() + timedelta(days=7)
            confirmation_last_date = batch.start_date + timedelta(days=20)
        else:
            reservation_last_date = batch.start_date
            confirmation_last_date = batch.start_date + timedelta(days=20)

    new_enrollment = Enrollment(
        user=user_profile,
        batch=batch,
        course_fee=batch.fees,
        reservation_last_date=reservation_last_date,
        confirmation_last_date=confirmation_last_date,
    )
    new_enrollment.save()

    # Render HTML template
    subject = 'My Python Trainer - Successful Course Enrollment'
    html_message = render_to_string('userapp/enrollment_email.html', {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'course_title': course_title,
        'batch_number': batch.batch_number,
        'start_date': batch.start_date,
        'tentative': "(Tentative)" if batch.tentative else "",
        'course_duration': batch.course.duration,
        'class_start_time': batch.start_time,
        'class_end_time': batch.end_time,
        'class_days': batch.days,
        'trainers': ', '.join([trainer.name + "(" + trainer.qualification.name + ', ' + trainer.college.name + ")" for trainer in
                               batch.trainers.all()]),
        'youtube_link': batch.youtube_link,
        'login_link': self.request.build_absolute_uri(reverse('userapp:login')),
        'reservation_last_date': reservation_last_date,
        'confirmation_last_date': confirmation_last_date
    })
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(
        subject,
        '',  # Leave plain-text body empty for an HTML-only email
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False
    )

# @method_decorator(login_required, name='dispatch')
# class NewCourseRegistration(View):
#     def dispatch(self, request, *args, **kwargs):
#         course_title = self.kwargs['course_title']
#         batch_name = self.kwargs['batch_name']
#         self.batch = get_object_or_404(Batch, batch_number=batch_name)
#         self.course = get_object_or_404(Course, title=course_title)
#
#
#         # Check if user is authenticated
#         if not request.user.is_authenticated:
#             return redirect(f"{reverse_lazy('userapp:login')}?next={reverse_lazy('userapp:new_courses_calendar_page')}")
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def get(self, request, *args, **kwargs):
#         user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)  # Create UserProfile if it doesn't exist
#         mobile_number = user_profile.mobile_number
#         email = request.user.email
#
#         registered_batch = Enrollment.objects.filter(user__user__email=email, batch__course__title=self.course.title).first()
#
#         # Check if the user is already registered and if the batch is active
#         if registered_batch:
#             if registered_batch.batch_name.status != 'freezed':
#                 messages.error(request, "You are already enrolled in an active batch. Cannot register in a new batch.")
#                 return redirect('userapp:applied_courses')
#
#         # Proceed with the registration
#         today = date.today()
#         if today >= self.batch.start_date:
#             reservation_last_date = datetime.now() + timedelta(days=2)
#             confirmation_last_date = datetime.now() + timedelta(days=10)
#         else:
#             if self.batch.start_date > today + timedelta(days=7):
#                 reservation_last_date = datetime.now() + timedelta(days=7)
#                 confirmation_last_date = self.batch.start_date + timedelta(days=20)
#             else:
#                 reservation_last_date = self.batch.start_date
#                 confirmation_last_date = self.batch.start_date + timedelta(days=20)
#
#         student_data = Enrollment(
#             user=user_profile,
#             batch=self.batch,
#             course_fee=self.batch.fees,
#             reservation_last_date=reservation_last_date,
#             confirmation_last_date=confirmation_last_date,
#         )
#         student_data.save()
#
#         return redirect('userapp:applied_courses')
        

class NewCoursesPageView(TemplateView):
    model = Course
    template_name = 'userapp/new-courses.html'
    context_object_name = 'courses'
    paginate_by = 3  # Paginate 3 courses per page

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True).order_by('title')
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                title__icontains=query
            ) | queryset.filter(
                description__icontains=query
            ) | queryset.filter(
                trainer__name__icontains=query  # Filter by trainer name
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Course.objects.filter(status=True).order_by('title')
        
        # Initialize a list to store courses that have batches
        courses_with_batches = []  # List to hold courses with active batches

        for course in courses:
            # Fetch the first trainer linked to the course
            trainers = course.trainers.all()

            if trainers.exists():  # Check if the course has any trainers associated
                # You can select the first trainer or iterate over all trainers (depends on your use case)
                trainer = trainers.first()  # Get the first trainer (if you're only interested in one)
                course.trainer_info = {
                    'name': trainer.name,
                    'rating': float(trainer.rating) if trainer.rating else 0.0
                }
            else:
                course.trainer_info = None  # No trainers associated

            # Fetch the first active batch linked to the course
            batch = Batch.objects.filter(course=course, status="open").first()
            
            # Only add the course to the list if a batch exists
            if batch:
                course.batch_info = batch  # Add the batch info to the course
                courses_with_batches.append(course)  # Add course to the filtered list


        # Only include courses with batches in the context
        context['courses'] = courses_with_batches
        return context

class NewCourseCalendarPageView(TemplateView):
    model = Course
    template_name = 'userapp/new-course-calendar.html'
    context_object_name = 'courses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all courses that have batches
        courses = Course.objects.filter(status=True).order_by('title')
        courses_with_batches = []
        
        # Annotate each course with batch and trainer details
        for course in courses:
            # Get trainer details (assuming multiple trainers)
            trainers = course.trainers.all()
            
            if trainers.exists():
                # You can collect all trainers or just the first one, depending on your requirement
                course.trainer_info = ', '.join([trainer.name for trainer in trainers])
            else:
                course.trainer_info = "No trainers available"
            
            # Get topic details
            topics = course.topic.all()
            if topics:
                course.topic_list = ' + '.join([topic.topic_name for topic in topics])
            else:
                course.topic_list = "No topics available"
            
            # Fetch all active batches for this course (not just the first)
            batches = Batch.objects.filter(course=course, status="open").order_by('start_date')
            
            # Add batches and course details to the course if there are active batches
            if batches.exists():
                course.batches = batches
                courses_with_batches.append(course)

                for batch in batches:
                    enrollments = Enrollment.objects.filter(batch=batch).order_by('enrollment_date')
                    batch.enrollments = enrollments
                    batch.enrollment_count = len(enrollments)

                    start_time = batch.start_time
                    end_time = batch.end_time

                    # Calculate the time difference using total seconds
                    if start_time and end_time:
                        # Convert time to total seconds since midnight
                        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
                        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
                        
                        # Calculate difference in seconds
                        time_difference_seconds = end_seconds - start_seconds

                        # Handle cases where the time difference is negative (crossing midnight)
                        if time_difference_seconds < 0:
                            time_difference_seconds += 24 * 3600  # Add 24 hours in seconds

                        # Convert to hours and minutes
                        hours = time_difference_seconds // 3600
                        fractional_minutes = (time_difference_seconds % 3600) / 3600
                        time_difference = hours + round(fractional_minutes, 1)
                        
                        # Attach time difference to batch object
                        batch.time_difference = time_difference
                    else:
                        # If time is not set properly, set default
                        batch.time_difference = "0"


        # Add the list of courses with batches to the context
        context['courses_with_batches'] = courses_with_batches

        return context


from django.views.generic import TemplateView
from userapp.models import Story

class NewStoriesPageView(TemplateView):
    template_name = 'userapp/new-stories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['approved_stories'] = CourseFeedback.objects.filter(status="Approved")
        return context

class NewContactPageView(TemplateView):
    template_name = 'userapp/new-contact.html'

class PrivacyPolicyPageView(TemplateView):
    template_name = 'userapp/privacy-policy.html'

class TermsConditionsPageView(TemplateView):
    template_name = 'userapp/terms-conditions.html'

class RefundPolicyPageView(TemplateView):
    template_name = 'userapp/refund-policy.html'

# @method_decorator(login_required, name='dispatch')
class AppliedCoursesView(ListView):
    model = Enrollment
    template_name = 'userapp/applied_courses.html'
    context_object_name = 'applied_courses'  # Context variable for the template

    def get_queryset(self):
        user_email = self.request.user.email
        if user_email:
            # Retrieve all applied courses for the user
            queryset = Enrollment.objects.filter(
                user__user__email=user_email
            ).select_related('batch').annotate(
                is_freezed=Case(
                    When(batch__status='freezed', then=True),
                    When(batch__status='created', then=True),
                    default=False,
                    output_field=BooleanField()
                ),
                can_pay=Case(
                    When(enrollment_status__in=['confirmed', 'pending', 'reserved'], then=True),
                    default=False,
                    output_field=BooleanField()
                )
            )
            return queryset

        return Enrollment.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollments = context['applied_courses']
        for enrollment in enrollments:
            start_time = enrollment.batch.start_time
            end_time = enrollment.batch.end_time
            enrollment.batch.class_per_week = len(enrollment.batch.days.split(","))
            enrollment.enrollment_status_display = {key: display for (key, display) in enrollment.ENROLLMENT_STATUS_CHOICES}.get(enrollment.enrollment_status)
            # Calculate the time difference using total seconds
            if start_time and end_time:
                # Convert time to total seconds since midnight
                start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
                end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

                # Calculate difference in seconds
                time_difference_seconds = end_seconds - start_seconds

                # Handle cases where the time difference is negative (crossing midnight)
                if time_difference_seconds < 0:
                    time_difference_seconds += 24 * 3600  # Add 24 hours in seconds

                # Convert to hours and minutes
                hours = time_difference_seconds // 3600
                fractional_minutes = (time_difference_seconds % 3600) / 3600
                time_difference = hours + round(fractional_minutes, 1)

                # Attach time difference to batch object
                enrollment.batch.time_difference = time_difference
            else:
                # If time is not set properly, set default
                enrollment.batch.time_difference = "0"

        context['users_with_batches'] = enrollments
        return context






class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'

# contact view
class ContactView(FormView):
    form_class = ContactForm
    template_name = 'userapp/contact.html'
    success_url = reverse_lazy('index_page')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CourseListView(ListView):
    model = Course
    template_name = 'userapp/courses.html'
    context_object_name = 'courses'
    paginate_by = 3  # Paginate 3 courses per page

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True).order_by('title')
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


# view for each courses
class CourseDetailView(DetailView):
    model = Course
    template_name = 'userapp/each_course.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

class PaymentSuccessView(TemplateView):
    template_name = 'userapp/payment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_id'] = self.request.GET.get('transaction_id', None)
        context['amount'] = self.request.GET.get('amount', None)
        return context

    def get(self, request, *args, **kwargs):
        transaction_id = self.request.GET.get('transaction_id', None)
        amount = self.request.GET.get('amount', None)

        if not transaction_id or not amount:
            return HttpResponseBadRequest("Bad Request: This page cannot be accessed.")

        return render(request, self.template_name, self.get_context_data())
    
class PaymentFailedView(TemplateView):
    template_name = 'userapp/payment_failed.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_message'] = self.request.GET.get('error_message', None)
        context['error_code'] = self.request.GET.get('error_code', None)
        return context

    def get(self, request, *args, **kwargs):
        error_message = self.request.GET.get('error_message', None)
        error_code = self.request.GET.get('error_code', None)

        if not error_message or not error_code:
            return HttpResponseBadRequest("Bad Request: This page cannot be accessed.")

        return render(request, self.template_name, self.get_context_data())

class MakePaymentView(FormView):
    form_class = PaymentForm
    template_name = 'userapp/make_payment.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if payment is already completed
        student = get_object_or_404(Enrollment, id=self.kwargs['course_id'], user__user__email=self.request.user.email)
        # Check if full payment is already made
        if student.full_status:
            return redirect('userapp:applied_courses')

        self.payment_type = kwargs['payment_type']  # Get payment type from URL
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get the student entry by course ID and email
        student = get_object_or_404(Enrollment, id=self.kwargs['course_id'], email=self.request.user.email)
        
        # Simulate the payment process based on the payment type
        if self.payment_type == 'advance':
            student.adv_status = True  # Update advance payment status
        elif self.payment_type == 'full':
            student.full_status = True  # Update full payment status
            student.full_transaction_id = ""
        
        student.save()
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_object_or_404(Enrollment, id=self.kwargs['course_id'], user__user__email=self.request.user.email)
        context['student'] = student

        # Determine amount based on payment type
        if self.payment_type == 'advance':
            amount = 500  # Define advance fee in your model
        elif self.payment_type == 'full':
            if student.adv_status == True:
                amount = student.course_fee - student.fee_discount - student.adv_fee
            else:
                amount =student.course_fee - student.fee_discount

        # Create Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create a Razorpay order
        payment_order = client.order.create({
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'payment_capture': '1'
        })
        
        callback_url = self.request.build_absolute_uri(reverse('userapp:payment_verification'))

        # Pass order details to the template
        context['razorpay_order_id'] = payment_order['id']
        context['razorpay_key'] = settings.RAZORPAY_KEY_ID
        context['amount'] = amount  # Set the dynamic amount
        context['callback_url'] = callback_url
        context['student_id'] = student.id
        context['payment_type'] = self.payment_type
        context['email'] = student.user.user.email
        context['mobile_number'] = student.user.mobile_number
        context['first_name'] = student.user.user.first_name
        context['last_name'] = student.user.user.last_name
        context['booking_amount'] = student.adv_fee
        context['course_fee'] = student.course_fee
        context['balance_amount'] = student.course_fee - student.fee_discount - student.adv_fee
        return context


@method_decorator(csrf_exempt, name='dispatch')  # Exempt from CSRF protection
class PaymentVerificationView(View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Check if the payment failed due to a bank error
        if 'error[code]' in data:
            error_code = data['error[code]']
            error_description = data['error[description]']
            # Manually construct the query parameters
            redirect_url = reverse('userapp:payment_failed')
            return redirect(f"{redirect_url}?error_code={error_code}&error_message={error_description}")
            # return JsonResponse({
            #     'status': 'failure',
            #     'message': f"Payment failed due to: {error_description} (Error Code: {error_code})"
            # }, status=400)

        # Ensure all necessary fields are present in the POST data
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'status': 'failure',
                    'message': f"Missing {field} in the request."
                }, status=400)

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            # Update the student’s payment status if verification is successful
            student = get_object_or_404(Enrollment, id=request.POST.get('student_id'), user__user__email=request.user.email)
            if data["payment_type"] == "advance" and not student.adv_status:
                student.adv_status = True
                student.enrollment_status = "reserved"
                student.adv_transaction_id = data['razorpay_payment_id']
                student.adv_payment_date = timezone.now()
            else:
                student.full_status = True
                student.enrollment_status = "confirmed"
                student.full_transaction_id = data['razorpay_payment_id']
                student.full_payment_date = timezone.now()
            # student.full_transaction_id = data['razorpay_payment_id']
            student.save()

            # On successful payment, return success status
            return JsonResponse({'status': 'success', 'transaction_id': data['razorpay_payment_id'], 'amount': data["amount"]})
            # redirect_url = reverse('userapp:payment_success')
            # return redirect(f"{redirect_url}?transaction_id={student.full_transaction_id}&amount={student.course_fee}")

        except razorpay.errors.SignatureVerificationError:
            # On signature verification failure
            redirect_url = reverse('userapp:payment_failed')
            return redirect(f"{redirect_url}?error_code=400&error_message=Payment verification failed.")
            # return JsonResponse({'status': 'failure', 'message': 'Payment verification failed.'}, status=400)

        # Catch all for other exceptions
        except Exception as e:
            redirect_url = reverse('userapp:payment_failed')
            return redirect(f"{redirect_url}?error_code=500&error_message=Error occurred during verification: {str(e)}")
            # return JsonResponse({'status': 'failure', 'message': f'Error occurred during verification: {str(e)}'}, status=500)
    
#password reset
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'userapp/password_reset_form.html'
    email_template_name = 'userapp/password_reset_email.html'
    success_url = reverse_lazy('userapp:password_reset_done')
    subject_template_name = 'userapp/password_reset_subject.txt'
    
    # Optional: Custom context for rendering the email
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_info'] = 'Some extra information'
        return context

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'userapp/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'userapp/password_reset_confirm.html'
    success_url = reverse_lazy('userapp:password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'userapp/password_reset_complete.html'


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'userapp/user_profile_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user profile for the logged-in user
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        context['user_profile'] = user_profile  # Add user profile to the context
        return context


class UserProfileEdit(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileEditForm
    template_name = 'userapp/user_profile_edit.html'
    success_url = reverse_lazy('userapp:user_profile_view')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            initial['mobile_number'] = user_profile.mobile_number
            initial['qualification'] = user_profile.qualification
            initial['position'] = user_profile.position
            initial['city'] = user_profile.city
            initial['country'] = user_profile.country
            initial['photo'] = user_profile.photo
        return initial

    def form_valid(self, form):
        user = form.save()

        # Handle password change (already managed in the form)
        new_password = form.cleaned_data.get('password')
        if new_password:
            # Ensure the session is updated after password change
            update_session_auth_hash(self.request, user)

        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


class BatchDetailView(DetailView):
    model = Batch
    template_name = 'userapp/batch_details.html'
    context_object_name = 'batch'

    def get_object(self):
        batch_number = self.kwargs.get('batch_number')
        return get_object_or_404(Batch, batch_number=batch_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = context['batch']
        course = batch.course
        topics = course.topic.all()
        context['topics'] = topics
        context['trainers'] = batch.trainers.all()
        context['enrollments'] = batch.dummy_registrations + len(Enrollment.objects.filter(batch__id=batch.id))
        youtube_link = batch.youtube_link
        if youtube_link and youtube_link.find('=') > -1:
            video_id = youtube_link[youtube_link.find('=')+1:]
            context['youtube_embed_url'] = r'https://www.youtube.com/embed//' + video_id
        else:
            context['youtube_embed_url'] = None

        return context

from django import forms
from .models import CourseFeedback

class CourseFeedbackForm(forms.ModelForm):
    class Meta:
        model = CourseFeedback
        fields = ['course', 'trainer', 'comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your feedback...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.5}),
        }
# views.py
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .models import CourseFeedback

class CourseFeedbackCreateView(CreateView):
    model = CourseFeedback
    form_class = CourseFeedbackForm
    template_name = 'userapp/feedback_create.html'
    success_url = reverse_lazy('userapp:feedback-success')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class FeedbackSuccessView(TemplateView):
    template_name = 'userapp/feedback_success.html'

from django.shortcuts import render
from django.views.generic import ListView
from .models import CourseFeedback

class CourseFeedbackListView(ListView):
    model = CourseFeedback
    template_name = 'userapp/stories.html'  # Your template file
    context_object_name = 'course_feedbacks'

    # Optionally, you can add custom logic if you want to filter or modify the queryset
    def get_queryset(self):
        return CourseFeedback.objects.all()
def stories_view(request):
    approved_stories = CourseFeedback.objects.filter(status="Approved")
    return render(request, 'userapp/new-stories.html', {
        'approved_stories': approved_stories,
    })


def add_discount(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        discount = request.POST.get('discount')
        if discount:
            enrollment.fee_discount = discount
            enrollment.save()
            messages.success(request, 'Discount added successfully!')
            return redirect('adminapp:enrollment_list')  # Redirect to wherever you list enrollments
    return render(request, 'userapp/add_discount.html', {'enrollment': enrollment})


