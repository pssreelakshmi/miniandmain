# Generated by Django 5.0.6 on 2024-08-01 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_contactmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='farmer',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='myapp.farmer'),
            preserve_default=False,
        ),
    ]
