from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Batch
from courseapp.models import Course
from .batch_form import BatchForm
from django.views.generic import UpdateView, DeleteView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from userapp.models import Enrollment

# Create your views here.
   
# create batch
class BatchFormView(LoginRequiredMixin, FormView):
    form_class = BatchForm
    template_name = 'batchapp/give_batch.html' 
    success_url = reverse_lazy('batchapp:batch_list')

    def form_valid(self, form):
        batch_number = form.cleaned_data.get('batch_number')

        # Check if batch number already exists
        if Batch.objects.filter(batch_number=batch_number).exists():
            messages.error(self.request, f'Batch number "{batch_number}" already exists. Please choose a unique batch number.')
            return self.form_invalid(form)  # Return the form with an error message

        # If batch number is unique, proceed with saving
        batch = form.save()
        messages.success(self.request, f'{batch.batch_number} batch created successfully')
        return super().form_valid(form)

# list batches
class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'batchapp/batches.html'
    context_object_name = 'batches'

    def post(self, request, *args, **kwargs):
        # Get the batch ID and action from the POST request
        batch_id = request.POST.get('batch_id')        
        action = request.POST.get('action')
        
        # Fetch the relevant batch object
        batch = get_object_or_404(Batch, id=batch_id)
        
        # Handle status change based on the button action
        if action == 'open_registrations':
            batch.status = 'open'  # Set status to Registrations Open
            messages.success(self.request, f'Registrations opened for Batch "{batch.batch_number}"!')
        elif action == 'freeze':
            batch.status = 'freezed'  # Set status to Freezed
            messages.warning(self.request, f'Batch "{batch.batch_number}" has been freezed. Enrollments are no longer allowed!')
        elif action == 'deactivate':
            batch.status = 'created'
        elif action == 'complete':
            batch.status = 'completed'
            #enrollments = batch.enrollment_set.all()
            enrollments = Enrollment.objects.filter(batch__id=batch_id)
            for enrollment in enrollments:
                enrollment.enrollment_status = 'closed'
                enrollment.save()

            messages.warning(self.request, f'Batch "{batch.batch_number}" has been completed. All its Enrollments are also moved to Closed!')

        batch.save()

        # Redirect to the same page after the status is changed
        return redirect('batchapp:batch_list') 
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('id')
        
        # Apply filters based on request parameters
        batch_filter = self.request.GET.get('batch')
        course_filter = self.request.GET.get('course')
        status_filter = self.request.GET.get('batch_status')

        if batch_filter:
            queryset = queryset.filter(batch_number=batch_filter)
        
        if course_filter:
            queryset = queryset.filter(course__title__icontains=course_filter, course__status=True)
        else:
            queryset = queryset.filter(course__status=True)  # Assuming `course` has a name field
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Annotate each batch with the total count and filtered counts
        queryset = queryset.annotate(
            total_students=Count('enrollment'),
            pending_students=Count('enrollment', filter=Q(enrollment__enrollment_status='pending')),
            reserved_students=Count('enrollment', filter=Q(enrollment__enrollment_status='reserved')),
            confirmed_students=Count('enrollment', filter=Q(enrollment__enrollment_status='confirmed')),
            deactivated_students=Count('enrollment', filter=Q(enrollment__enrollment_status='deactivated')),
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        # Get the base context data from the parent class
        context = super().get_context_data(**kwargs)

        # Add additional context data for dropdown options and selected values
        context['batch_list'] = Batch.objects.all()
        context['courses'] = Course.objects.filter(status=True)
        context['batch_status'] = Batch.STATUS_CHOICES

        context['selected_batch'] = self.request.GET.get('batch', '')
        context['selected_course'] = self.request.GET.get('course', '')
        context['selected_status'] = self.request.GET.get('batch_status', '')

        return context

# each batches
class BatchDetailView(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = 'batchapp/batch_details.html'
    context_object_name = 'each_bch'

    def get_object(self):
        batch_id = self.kwargs.get('batch_id')
        return get_object_or_404(Batch, pk=batch_id)

# delete a batch - JC Added message
class BatchDelete(LoginRequiredMixin, DeleteView):
    model = Batch
    success_url = reverse_lazy('batchapp:batch_list')

    def form_valid(self, form):
        batch_no = self.get_object().batch_number
        messages.success(self.request, f'Batch "{batch_no}" deleted successfully.')
        return super().form_valid(form)

# update batch
class BatchEdit(LoginRequiredMixin, UpdateView):
    model = Batch
    form_class = BatchForm
    success_url = reverse_lazy('batchapp:batch_list')

    def get_form(self, form_class=None):
        form = super(BatchEdit, self).get_form(form_class)
        batch = self.get_object()

        # Populate the form with the existing batch data
        if batch.days:
            form.initial['days'] = batch.days.split(',')  # Populate days as a list for checkboxes

        form.initial['start_time'] = batch.start_time
        form.initial['end_time'] = batch.end_time
        form.initial['status'] = batch.status

        # Restrict status choices based on the current status
        if batch.status == 'created':
            form.fields['status'].choices = [
                ('created', 'Created'),
                ('open', 'Registrations Open'),
            ]
        elif batch.status == 'open':
            form.fields['status'].choices = [
                ('created', 'Created'),
                ('open', 'Registrations Open'),
                ('freezed', 'Freezed')
            ]
        elif batch.status == 'freezed':
            form.fields['status'].choices = [
                ('open', 'Registrations Open'),
                ('freezed', 'Freezed')
            ]  # No further status changes allowed

        return form

    def form_valid(self, form):
        batch = form.save(commit=False)

        # Handle messages for status changes
        if batch.status == 'open':
            messages.success(self.request, f'Registrations opened for Batch "{batch.batch_number}"!')
        elif batch.status == 'freezed':
            messages.warning(self.request, f'Batch "{batch.batch_number}" has been freezed. Registrations are no longer allowed!')
        elif batch.status == 'created':
            messages.info(self.request, f'Batch "{batch.batch_number}" is now in Created status.')

        batch.save()
        return super().form_valid(form)

