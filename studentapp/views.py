from .models import Student, Course
from batchapp.models import Batch
from django.views.generic import ListView, DetailView, UpdateView
from userapp.models import Enrollment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from userapp.models import UserProfile
from django.db.models import Count, Q

class ViewRegistrationsListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'studentapp/registrations.html'
    context_object_name = 'registrations_data'

    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset().order_by('id')        

        # # Annotate each user with the batches enrolled.
        # queryset = queryset.annotate(
        #     all_enrollments=Count('enrollment'),
        #     pending_enrollments=Count('enrollment', filter=Q(enrollment__enrollment_status='pending')),
        #     deactivated_enrollments=Count('enrollment', filter=Q(enrollment__enrollment_status='deactivated')),
        #     seat_reserved_enrollments=Count('enrollment', filter=Q(enrollment__enrollment_status='reserved')),
        #     seat_confirmed_enrollments=Count('enrollment', filter=Q(enrollment__enrollment_status='confirmed')),
        # )



        filtered_set = []
        for user in queryset:
            if user.user.groups.filter(name='Student'):
                all_enrollments = user.enrollments.all()
                user.all_enrollments = all_enrollments
                user.pending_enrollments = all_enrollments.filter(enrollment_status='pending')
                user.deactivated_enrollments = all_enrollments.filter(enrollment_status='deactivated')
                user.reserved_enrollments = all_enrollments.filter(enrollment_status='reserved')
                user.confirmed_enrollments = all_enrollments.filter(enrollment_status='confirmed')
                user.closed_enrollments = all_enrollments.filter(enrollment_status='closed')
                user.need_attention_enrollments = "NA" if len(all_enrollments) == len(user.confirmed_enrollments) + len(user.closed_enrollments) else ""
                filtered_set.append(user)

        return filtered_set


class ViewEnrollmentListView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'studentapp/students.html'
    context_object_name = 'students_data'
    # paginate_by = 8

    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset().order_by('id')
        
        # Retrieve filter parameters from GET request
        batch = self.request.GET.get('batch')
        course = self.request.GET.get('course')
        enrollment_status = self.request.GET.get('enrollment_status')        

        # Apply filters conditionally
        if batch:
            queryset = queryset.filter(batch__batch_number=batch)  # Corrected filter
        if course:
            queryset = queryset.filter(batch__course__title=course)
        if enrollment_status:
            queryset = queryset.filter(enrollment_status=enrollment_status)
        if (batch is None or batch == "") and (course is None or course == "") and (enrollment_status is None or enrollment_status == ""):
            queryset = queryset.filter(batch__status='open')

        return queryset

    def post(self, request, *args, **kwargs):
        # Get the Enrollment ID and action from the POST request
        enrollment_id = request.POST.get('enrollment_id')
        action = request.POST.get('action')

        # Fetch the relevant enrollment object
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        # Handle status change based on the button action
        if action == 'MovePaymentPending':
            enrollment.enrollment_status = 'pending'  # Set status to Registrations Open
            messages.success(self.request, f'Enrollment is Moved to "Payment Pending" for "{enrollment.user.user.first_name} {enrollment.user.user.last_name} ({enrollment.user.user.email})"!')
        elif action == 'MoveDeactivate':
            enrollment.enrollment_status = 'deactivated'  # Set status to Reserved
            messages.warning(self.request, f'Enrollment is "Deactivated" for "{enrollment.user.user.first_name} {enrollment.user.user.last_name} ({enrollment.user.user.email})"!')
        elif action == 'MoveSeatReserved':
            enrollment.adv_status = True
            enrollment.adv_transaction_id = 'Offline'
            enrollment.adv_payment_date = datetime.now()
            enrollment.enrollment_status = 'reserved'  # Set status to Reserved
            messages.warning(self.request, f'Enrollment is Moved to "Seat Reserved" for "{enrollment.user.user.first_name} {enrollment.user.user.last_name} ({enrollment.user.user.email})"!')
        elif action == 'MoveSeatConfirmed':
            enrollment.full_status = True
            enrollment.full_transaction_id = 'Offline'
            enrollment.full_payment_date = datetime.now()
            enrollment.enrollment_status = 'confirmed'  # Set status to Reserved
            messages.warning(self.request, f'Enrollment is Moved to "Seat Confirmed" for "{enrollment.user.user.first_name} {enrollment.user.user.last_name} ({enrollment.user.user.email})"!')
        elif action == 'AccessProvided':
            enrollment.all_links_accessible = True  # Set status to Reserved
            messages.warning(self.request, f'Enrollment is Moved to "Seat Confirmed" for "{enrollment.user.user.first_name} {enrollment.user.user.last_name} ({enrollment.user.user.email})"!')

        enrollment.save()

        # Redirect to the same page after the status is changed
        return redirect('studentapp:view_students')


    def get_context_data(self, **kwargs):
        # Get the base context data from the parent class
        context = super().get_context_data(**kwargs)

        # Add additional context data for dropdown options and selected values
        context['batches'] = Batch.objects.filter(status='open') 
        context['courses'] = Course.objects.filter(status=True)
        context['enrollment_statuses'] = Enrollment.ENROLLMENT_STATUS_CHOICES

        context['selected_batch'] = self.request.GET.get('batch', '')
        context['selected_course'] = self.request.GET.get('course', '')
        context['selected_enrollment_status'] = self.request.GET.get('enrollment_status', '')

        return context


# each students
class EachStudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'studentapp/each_stud_details.html'
    context_object_name = 'stud'
    pk_url_kwarg = 'stud_id'


# forms.py
from django import forms
from userapp.models import Enrollment

class EnrollmentDiscountForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['fee_discount']  # We allow editing only 'fee_discount'

        widgets = {
            'fee_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Discount Amount',
                'min': '0',
            }),
        }
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from userapp.models import Enrollment

def add_discount(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        form = EnrollmentDiscountForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            # Optionally add a success message
            return redirect('studentapp:view_students')
    else:
        form = EnrollmentDiscountForm(instance=enrollment)

    return render(request, 'studentapp/add_discount.html', {'form': form, 'enrollment': enrollment})



