from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from .adminforms import RegisterForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, FormView, UpdateView
from django.contrib.auth.models import User
from userapp.forms import AdminProfileEditForm
from userapp.models import UserProfile

# Create your views here.

class RegisterView(FormView):
    template_name = 'adminapp/register.html'  # Path to your template
    form_class = RegisterForm  # Your custom registration form
    success_url = reverse_lazy('userapp:login')  # Redirect after successful registration

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


class AdminHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'adminapp/home.html'

    # This method restricts the access to users in the 'Admin' group
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

    # Handle unauthorized access (users who are not Admin)
    def handle_no_permission(self):
        return redirect('userapp:no-access')  # Redirect to a "no access" page or login page
 
class AdminProfileEdit(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AdminProfileEditForm
    template_name = 'adminapp/admin_profile.html'
    success_url = reverse_lazy('adminapp:admin_view')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            initial['mobile_number'] = user_profile.mobile_number
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

class AdminProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'adminapp/admin_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user profile for the logged-in user
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        context['user_profile'] = user_profile  # Add user profile to the context
        return context
