# Generated by Django 2.0.5 on 2018-07-12 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qbconnect', '0004_auto_20180607_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userconnection',
            name='access_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userconnection',
            name='company_id',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='userconnection',
            name='consumer_key',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userconnection',
            name='consumer_secret',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userconnection',
            name='refresh_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
