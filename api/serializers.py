from django.contrib.auth.models import User
from rest_framework import serializers, validators
from .models import Profile, Order
import random

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "email", "first_name", "last_name")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
            },
        }
    
    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')

        if User.objects.filter(email=email):
            raise serializers.ValidationError("L'utente con questa email esiste già")
        else:
            user = User.objects.create_user(**validated_data)
            r = random.randint(1, 10)
            profile = Profile.objects.create(user=user, balanceBTC=r, availableBalanceBTC=r)
            return user


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("type", "currency", "price", "quantity")

    def create(self, validated_data):
        order = Order.objects.create(**validated_data, quantityToPerformed = validated_data["quantity"])
        return order
    