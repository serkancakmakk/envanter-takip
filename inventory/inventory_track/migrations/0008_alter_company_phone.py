# Generated by Django 5.1.4 on 2025-01-06 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_track', '0007_alter_brand_table_alter_category_table_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
