# Generated by Django 4.2.2 on 2023-10-31 13:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('datacenter', '0008_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='buy_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время покупки'),
        ),
    ]
