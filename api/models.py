from django.db import models

from djongo.models.fields import ObjectIdField, Field
from django.contrib.auth.models import User
from django.conf import settings

class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    subprofiles = models.Field(default=[])
    balanceBTC = models.FloatField(default=0)
    balanceUSD = models.FloatField(default=0)
    availableBalanceBTC = models.FloatField(default=0)
    availableBalanceUSD = models.FloatField(default=0)
    profit = models.FloatField(default=0)

    def __str__(self):
        return str(self.user.username)
    
class Order(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=4, choices=[('buy', 'buy'), ('sell', 'sell')])
    currency = models.CharField(max_length=8, choices=[('BTC', 'BTC')])
    price = models.FloatField()
    quantity = models.FloatField()
    quantityToPerformed = models.FloatField()
    totalPriceExecuted = models.FloatField(default=0) #Prezzo totale di acquisto eseguito su più quantità separate acquistate
    status = models.CharField(max_length=8, default="active",  choices=[('active', 'active'), ('inactive', 'inactive'), ('executed', 'executed')])

    def __str__(self):
        return self.datetime.strftime('%Y/%m/%d - %H:%M')