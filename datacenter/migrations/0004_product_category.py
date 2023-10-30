# Generated by Django 4.2.6 on 2023-10-27 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datacenter', '0003_setting_delete_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='datacenter.category', verbose_name='К какой категории привязан'),
            preserve_default=False,
        ),
    ]
