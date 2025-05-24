from django.shortcuts import render
from django.urls import resolve

class RestrictStudentAccessMiddleware:
    """
    Middleware to restrict Student users from accessing certain apps.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print(request.user.groups.filter(name='Admin').exists())
        # print(request.user.is_authenticated)
        # Ensure the user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Define restricted apps
            restricted_apps = ['batchapp', 'courseapp', 'trainers', 'topicapp', 'courseapp', 'studentapp']
            
            # Get the current app name from the URL
            current_app = resolve(request.path).app_name
            try:
                # If the user is a Student and is accessing restricted app, redirect them
                if request.user.groups.filter(name='Student').exists() and current_app in restricted_apps:
                    return render(request, template_name='userapp/no_access.html')
            except Exception as e:
                print(e)

        # Process the request normally if no issues
        response = self.get_response(request)
        return response