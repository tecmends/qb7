# Generated by Django 2.0.5 on 2018-07-12 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0012_csvfileresults_customer_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchInvoiceResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('S', 'Success'), ('F', 'Failed'), ('W', 'Warning')], default='S', max_length=50)),
                ('invoice_id', models.CharField(max_length=500, null=True)),
                ('customer_id', models.CharField(max_length=500, null=True)),
                ('error_message', models.TextField(null=True)),
                ('error_response', models.TextField(null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='csvfileresults',
            name='csv_file',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='invoice.CsvFile'),
        ),
    ]
