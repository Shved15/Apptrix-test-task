# Generated by Django 3.2.20 on 2023-07-08 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to='avatars/'),
        ),
    ]
