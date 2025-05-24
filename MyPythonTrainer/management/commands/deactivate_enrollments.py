from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils.timezone import now
from userapp.models import Enrollment

class Command(BaseCommand):
    help = "Deactivate users with pending status for more than 7 days"

    def handle(self, *args, **kwargs):
        threshold_date = now() - timedelta(days=7)
        students_to_deactivate = Enrollment.objects.filter(
            enrollment_status='pending',
            enrollment_date__lt=threshold_date
        )
        count = students_to_deactivate.update(enrollment_status='deactivated')
        
        current_datetime = now().strftime('%Y-%m-%d')
        
        self.stdout.write(f"[{current_datetime}] {count} enrollment(s) were deactivated.")