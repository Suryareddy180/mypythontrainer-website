from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Course, CourseForm
from django.views.generic import View, UpdateView, DeleteView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CoursesFormView(LoginRequiredMixin,FormView):
    form_class = CourseForm
    template_name = 'courseapp/course.html' 
    success_url = reverse_lazy('courseapp:course_list')
    login_url = '/login/'

    def form_valid(self, form):
        course = form.save(commit=False)
        # print(course.topic)
        
        if 'uploaded_file' in self.request.FILES:
            uploaded_file = self.request.FILES['uploaded_file']
            course_title_clean = course.title.replace(' ', '_').lower() 
            filename = f"{course_title_clean}_{uploaded_file.name}"
            
            # Assign the custom filename to the uploaded file field
            course.uploaded_file.save(filename, uploaded_file)

        course.save()  # Save the course with the file
        # print("Selected topics:", form.cleaned_data.get('topic'))

        topics = form.cleaned_data.get('topic')  # Retrieve selected topics from the form
        if topics:
            course.topic.set(topics)

        trainers = form.cleaned_data.get('trainers')  # Retrieve selected topics from the form
        if trainers:
            course.trainers.set(trainers)
        
        num = course.title
        messages.success(self.request, f'{num} course created successfully')
        return super().form_valid(form)
    
# course list
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courseapp/courselist.html'
    context_object_name = 'course'

    def post(self, request, *args, **kwargs):
        # Handle the status change when a checkbox is toggled
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        course.status = not course.status  # Toggle the status
        course.save()

        # Redirect to the same page after the status is toggled
        return redirect('courseapp:course_list') 
    
    def get_queryset(self):
        queryset = super().get_queryset().all().order_by('title')
        return queryset
    
# each courses
class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courseapp/course_details.html'
    context_object_name = 'each_one'

    def get_object(self):
        course_id = self.kwargs.get('course_id')
        return get_object_or_404(Course, pk=course_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

# delete a course

class CourseToggleStatus(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs['pk'])
        if course.batch_set.exists():
            batch_names = ", ".join([batch.batch_number for batch in course.batch_set.all()])
            messages.error(request, f'One or more batches ({batch_names}) are created and/or opened registrations for "{course.title}". You can\'t deactivate the course now.')
            return redirect('courseapp:course_list')  # Redirect back to the trainer view page
        course.status = not course.status
        course.save()
        if course.status:
            messages.success(request, f'Course "{course.title}" has been activated.')
        else:
            messages.success(request, f'Course "{course.title}" has been deactivated.')
        return redirect('courseapp:course_list')
    
# update a course

