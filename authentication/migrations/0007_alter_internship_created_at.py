# Generated by Django 5.0.6 on 2024-05-26 16:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_alter_internship_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internship',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
