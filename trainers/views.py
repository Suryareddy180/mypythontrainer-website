from django.shortcuts import get_object_or_404, redirect
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from .models import Trainer, Degree, College, Qualification, Organization, Award
from django.urls import reverse_lazy, reverse
from django.views.generic import View, UpdateView, DeleteView, FormView, ListView, DetailView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# create a model form
class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = '__all__'
        exclude = ['status']

    def __init__(self, *args, **kwargs):
        super(TrainerForm, self).__init__(*args, **kwargs)
        # Make the country_code field uneditable
        self.fields['country_code'].disabled = True

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # If editing an existing trainer (not creating a new one)
        if self.instance and self.instance.pk:
            # Check if the email has been changed
            if email and Trainer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('A trainer with this email already exists.')
        else:
            # For new trainer creation, ensure the email is unique
            if Trainer.objects.filter(email=email).exists():
                raise ValidationError('A trainer with this email already exists.')

        return email


# Create your views here.
class TrainerFormView(LoginRequiredMixin, FormView):
    form_class = TrainerForm
    template_name = 'trainers/trainer.html'
    success_url = reverse_lazy('trainers:trainer_view')

    def form_valid(self, form):
        trainer = form.save()
        trainer_name = trainer.name
        messages.success(self.request, f'Trainer "{trainer_name}" created successfully')
        return super().form_valid(form)


# list trainers
class TrainersListView(LoginRequiredMixin, ListView):
    model = Trainer
    context_object_name = 'data'
    template_name = 'trainers/trainers.html'
    ordering = ['-name']

    def post(self, request, *args, **kwargs):
        # Handle the status change when a checkbox is toggled
        trainer_id = request.POST.get('trainer_id')
        trainer = get_object_or_404(Trainer, id=trainer_id)
        trainer.status = not trainer.status  # Toggle the status
        trainer.save()

        # Redirect to the same page after the status is toggled
        return redirect('trainers:trainer_view')

    def get_queryset(self):
        queryset = super().get_queryset().all().order_by('name')
        return queryset


# view each trainer details
class TrainerDetailView(LoginRequiredMixin, DetailView):
    model = Trainer
    template_name = 'trainers/each_trainer.html'
    context_object_name = 'new'

    def get_object(self):
        trainer_id = self.kwargs.get('pk')
        # print(trainer_id)
        return get_object_or_404(Trainer, pk=trainer_id)


# remove trainer


class TrainerToggleStatus(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        trainer = Trainer.objects.get(pk=self.kwargs['pk'])  # Fetch the trainer by primary key

        # Check if the trainer is assigned to any courses
        if trainer.course_set.exists():
            course_names = ", ".join([course.title for course in trainer.course_set.all()])
            messages.error(request,
                           f'Trainer "{trainer.name}" is assigned to "{course_names}". Please untag them from the course(s) to deactivate.')
            return redirect('trainers:trainer_view')  # Redirect back to the trainer view page

        # Toggle the status
        trainer.status = not trainer.status
        trainer.save()

        # Send a success message
        if trainer.status:
            messages.success(request, f'Trainer "{trainer.name}" has been activated.')
        else:
            messages.success(request, f'Trainer "{trainer.name}" has been deactivated.')

        # Redirect back to the trainer view
        return redirect('trainers:trainer_view')


# edit a trainer


# class TrainerToggleStatus(LoginRequiredMixin, View):
#     def post(self, request, *args, **hytrewq
#         trainer = Trainer.objects.get(pk=kwargs['pk'])

#         # Toggle the trainer's status
#         if trainer.status:  # If active, trying to deactivate
#             if trainer.course_set.exists():  # Check if trainer is assigned to any course
#                 course_names = ", ".join([course.title for course in trainer.course_set.all()])
#                 messages.error(self.request, f'Trainer "{trainer.name}" is already assigned to "{course_names}". Please untag them from the course(s) to deactivate.')
#                 return redirect(reverse('trainers:trainer_view'))  # Redirect back to trainer list

#             # Deactivate the trainer
#             trainer.status = False
#             messages.success(self.request, f'Trainer "{trainer.name}" has been deactivated.')
#         else:
#             # Activate the trainer
#             trainer.status = True
#             messages.success(self.request, f'Trainer "{trainer.name}" has been activated.')

#         trainer.save()
#         return redirect(reverse('trainers:trainer_view'))  # Redirect back to the trainer list after action

class DegreeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'trainers/Degree.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = "__all__"


class DegreeAdd(FormView):
    form_class = DegreeForm
    template_name = "trainers/DegreeAdd.html"
    success_url = reverse_lazy('trainers:DegreeSuccess')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class DegreeSuccess(TemplateView):
    template_name = 'trainers/DegreeSuccess.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msg'] = "A NEW DEGREE IS ADDED SUCCESSFULLY"
        return context


class DegreeList(ListView):
    template_name = "trainers/DegreeList.html"
    model = Degree
    context_object_name = "deg"


"______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________"


class CollegeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'trainers/College.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = "__all__"


class CollegeAdd(FormView):
    form_class = CollegeForm
    template_name = "trainers/CollegeAdd.html"
    success_url = reverse_lazy("trainers:CollegeSuccess")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CollegeSuccess(TemplateView):
    template_name = "trainers/CollegeSuccess.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msg'] = "A NEW COLLEGE IS ADDED SUCCESSFULLY"
        return context


class CollegeList(ListView):
    template_name = "trainers/CollegeList.html"
    model = College
    context_object_name = "clg"


"________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________"


class QualificationsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'trainers/Qualification.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = "__all__"


class QualificationAdd(FormView):
    form_class = QualificationForm
    template_name = "trainers/QualificationAdd.html"
    success_url = reverse_lazy("trainers:QualificationSuccess")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class QualificationSuccess(TemplateView):
    template_name = "trainers/QualificationSuccess.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msg'] = "A QUALIFICATION IS ADDED SUCCESSFULLY"
        return context


class QualificationList(ListView):
    template_name = "trainers/QualificationList.html"
    model = Qualification
    context_object_name = "qua"


"_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________"


class OrganizationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'trainers/Organization.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationAdd(FormView):
    form_class = OrganizationForm
    template_name = "trainers/OrganizationAdd.html"
    success_url = reverse_lazy("trainers:OrganizationSuccess")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OrganizationSuccess(TemplateView):
    template_name = "trainers/OrganizationSuccess.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msg'] = "A NEW ORGANIZATION IS ADDED SUCCESSFULLY"
        return context


class OrganizationList(ListView):
    template_name = "trainers/OrganizationList.html"
    model = Organization
    context_object_name = "org"


"______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________"


class AwardsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'trainers/Award.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = "__all__"


class AwardAdd(FormView):
    form_class = AwardForm
    template_name = "trainers/AwardAdd.html"
    success_url = reverse_lazy("trainers:AwardSuccess")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AwardSuccess(TemplateView):
    template_name = "trainers/AwardSuccess.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msg'] = "A NEW AWARD IS ADDED SUCCESSFULLY"
        return context


class AwardList(ListView):
    template_name = "trainers/AwardList.html"
    model = Award
    context_object_name = "awd"


from userapp.models import Story, CourseFeedback

class CourseFeedbackListView(ListView):
    model = CourseFeedback
    template_name = 'trainers/stories.html'  # Your template file
    context_object_name = 'course_feedbacks'

    # Optionally, you can add custom logic if you want to filter or modify the queryset
    def get_queryset(self):
        return CourseFeedback.objects.all()

from userapp.models import CourseFeedback
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def approve_feedback(request, feedback_id):
    feedback = get_object_or_404(CourseFeedback, id=feedback_id)
    feedback.status = 'Approved'
    feedback.save()
    messages.success(request, "✅ Feedback approved successfully!")
    return redirect('trainers:stories')

def reject_feedback(request, feedback_id):
    feedback = get_object_or_404(CourseFeedback, id=feedback_id)
    feedback.status = 'Rejected'
    feedback.save()
    messages.warning(request, "⚠️ Feedback rejected successfully!")
    return redirect('trainers:stories')