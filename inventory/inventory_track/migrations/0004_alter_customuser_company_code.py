# Generated by Django 5.1.4 on 2025-01-05 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_track', '0003_customuser_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='company_code',
            field=models.CharField(),
        ),
    ]
