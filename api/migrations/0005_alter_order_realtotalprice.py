# Generated by Django 4.1.8 on 2023-04-13 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_sellingprice_order_realtotalprice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='realTotalPrice',
            field=models.FloatField(default=0),
        ),
    ]
