# Generated by Django 4.2.2 on 2023-10-29 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacenter', '0004_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='source',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Источник'),
        ),
    ]