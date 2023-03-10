# Generated by Django 4.1.4 on 2022-12-27 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='total_price',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
