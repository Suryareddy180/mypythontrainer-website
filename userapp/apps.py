from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UserappConfig(AppConfig):
    name = 'userapp'
    
    def ready(self):
        # Register the post_migrate signal
        post_migrate.connect(create_groups, sender=self)


def create_groups(sender, **kwargs):
    # Dynamically import Group to avoid accessing it too early
    from django.contrib.auth.models import Group

    # Check if the 'Admin' group exists; if not, create it
    admin_group, created = Group.objects.get_or_create(name='Admin')
    if created:
        print("Created 'Admin' group.")
    
    # Check if the 'Student' group exists; if not, create it
    student_group, created = Group.objects.get_or_create(name='Student')
    if created:
        print("Created 'Student' group.")
