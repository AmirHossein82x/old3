# Generated by Django 4.1.3 on 2022-11-30 10:54

from django.db import migrations, models
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_product_inventory_alter_product_promotions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=255, validators=[store.models.length_validator]),
        ),
    ]
