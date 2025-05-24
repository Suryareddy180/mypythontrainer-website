from django.shortcuts import get_object_or_404, redirect
from django.forms import ModelForm
from django.contrib import messages
from .models import Topic
from django.views.generic import View, UpdateView, DeleteView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'
        exclude = ['status']


# create topic
class TopicFormView(LoginRequiredMixin, FormView):
    form_class = TopicForm
    template_name = 'topicapp/give_topic.html' 
    success_url = reverse_lazy('topicapp:topic_list')

    def form_valid(self, form):
        # Assuming your TopicForm has a 'topic_name' field
        topic_name = form.cleaned_data.get('topic_name')

        # Check if the topic_name already exists
        if Topic.objects.filter(topic_name=topic_name).exists():
            messages.error(self.request, f'Topic "{topic_name}" already exists.')
            return self.form_invalid(form)  # Return the form with an error message

        # If the topic doesn't exist, save the new record
        topic = form.save()
        messages.success(self.request, f'Topic "{topic.topic_name}" created successfully.')
        return super().form_valid(form)

# list topics
class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'topicapp/topics.html'
    context_object_name = 'topics'

    def post(self, request, *args, **kwargs):
        # Handle the status change when a checkbox is toggled
        topic_id = request.POST.get('topic_id')
        topic = get_object_or_404(Topic, id=topic_id)
        topic.status = not topic.status  # Toggle the status
        topic.save()

        # Redirect to the same page after the status is toggled
        return redirect('topicapp:topic_list') 
    
    def get_queryset(self):
        queryset = super().get_queryset().all()
        return queryset

# each topics
class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic
    template_name = 'topicapp/topic_details.html'
    context_object_name = 'each_tpk'

    def get_object(self):
        topic_id = self.kwargs.get('topic_id')
        # print(topic_id)
        return get_object_or_404(Topic, pk=topic_id)

# delete Topic - JC Added message


class TopicToggleStatus(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        topic = Topic.objects.get(pk=self.kwargs['pk'])
        if topic.course_set.exists():
            course_names = ", ".join([course.title for course in topic.course_set.all()])
            messages.error(request, f'Topic "{topic.topic_name}" is assigned to "{course_names}". Please untag them from the course(s) to deactivate.')
            return redirect('topicapp:topic_list')
        topic.status = not topic.status
        topic.save()

        # Send a success message
        if topic.status:
            messages.success(request, f'{topic.topic_name} has been activated.')
        else:
            messages.success(request, f'{topic.topic_name} has been deactivated.')

        return redirect('topicapp:topic_list')

# update Topic

