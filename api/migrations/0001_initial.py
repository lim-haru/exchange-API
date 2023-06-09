# Generated by Django 4.1.8 on 2023-04-11 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('ips', models.Field(default=[])),
                ('subprofiles', models.Field(default=[])),
                ('balanceBTC', models.FloatField(default=4)),
                ('balanceUSD', models.FloatField(default=0)),
                ('availableBalanceBTC', models.FloatField(default=4)),
                ('availableBalanceUSD', models.FloatField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], max_length=4)),
                ('currency', models.CharField(choices=[('BTC', 'BTC')], max_length=8)),
                ('price', models.FloatField()),
                ('quantity', models.FloatField()),
                ('quantityToPerformed', models.FloatField()),
                ('status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive'), ('executed', 'executed')], default='active', max_length=8)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
