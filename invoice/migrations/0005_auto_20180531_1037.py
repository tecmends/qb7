# Generated by Django 2.0.5 on 2018-05-31 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_auto_20180531_0430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvfile',
            name='status',
            field=models.CharField(choices=[('Received', 'R'), ('InProgress', 'Q'), ('Completed', 'C'), ('Failed', 'F')], default='R    ', max_length=50),
        ),
    ]
