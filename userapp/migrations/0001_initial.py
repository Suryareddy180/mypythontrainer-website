# Generated by Django 5.2 on 2025-04-27 15:49

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('batchapp', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone', models.IntegerField(unique=True)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adv_status', models.BooleanField(default=False)),
                ('full_status', models.BooleanField(default=False)),
                ('adv_fee', models.DecimalField(blank=True, decimal_places=2, default=500, max_digits=5, null=True)),
                ('course_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fee_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('adv_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('full_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('enrollment_status', models.CharField(choices=[('pending', 'Payment Pending'), ('deactivated', 'Auto Cancelled'), ('reserved', 'Seat Reserved'), ('confirmed', 'Seat Confirmed'), ('closed', 'Closed')], default='pending', max_length=50)),
                ('all_links_accessible', models.BooleanField(default=False)),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('reservation_last_date', models.DateTimeField(blank=True, null=True)),
                ('adv_payment_date', models.DateTimeField(blank=True, null=True)),
                ('confirmation_last_date', models.DateTimeField(blank=True, null=True)),
                ('full_payment_date', models.DateTimeField(blank=True, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batchapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('', ''), ('Text', 'Text'), ('Video', 'Video')], max_length=20)),
                ('comments', models.CharField(max_length=1000)),
                ('rating', models.FloatField(choices=[(1, 1), (1.5, 1.5), (2, 2), (2.5, 2.5), (3, 3), (3.5, 3.5), (4, 4), (4.5, 4.5), (5, 5)])),
                ('status', models.CharField(choices=[('', ''), ('Create', 'Created'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Published', 'Published')], max_length=20)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.enrollment')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(default='091', max_length=3)),
                ('mobile_number', models.CharField(default='', max_length=15)),
                ('qualification', models.CharField(choices=[('Secondary Schooler', 'School/10th/below 10th class'), ('High Schooler', 'High School/Intermediate'), ('BCA', 'BCA'), ('B.E', 'B.E'), ('B.Sc', 'B.Sc'), ('B.Tech', 'B.Tech'), ('MBA', 'MBA'), ('MCA', 'MCA'), ('M.E', 'M.E'), ('M.Sc', 'M.Sc'), ('M.Tech', 'M.Tech'), ('Other', 'Any Other Qualification')], max_length=30)),
                ('city', models.CharField(default='', max_length=30)),
                ('country', models.CharField(default='', max_length=30)),
                ('position', models.CharField(choices=[('', ''), ('Student', 'Student'), ('IT Job Aspirant', 'IT Job Aspirant'), ('Non IT Professional', 'Non IT Professional'), ('IT Professional', 'IT Professional')], default='', max_length=30)),
                ('photo', models.ImageField(default='', upload_to='user_photos/', verbose_name='Photo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='enrollment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='userapp.userprofile'),
        ),
    ]
