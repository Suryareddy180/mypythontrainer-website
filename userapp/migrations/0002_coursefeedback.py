# Generated by Django 5.1.7 on 2025-04-28 15:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseapp', '0002_alter_course_image'),
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courseapp.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.enrollment')),
            ],
        ),
    ]
