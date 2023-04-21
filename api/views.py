from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import RegisterSerializer, OrderSerializer
from .models import Profile, Order
from django.db.models import Q
from bson.objectid import ObjectId
from .utils import start_order
from django.contrib.auth import authenticate


@api_view(['POST'])
def login(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token = Token.objects.get(user=user)
    return Response({
        'user_data': serialize_user(user),
        'token': str(token)
    })
        

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user_info": serialize_user(user),
            "token": str(token)
        })


@api_view(['GET'])
def get_user(request):
    if 'username' in request.data and 'password' in request.data:
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
    else:
        user = request.user
    if user.is_authenticated:
        token = Token.objects.get(user=user)
        profile = Profile.objects.get(user=user)
        orders = Order.objects.filter(profile=user)
        if 'id' in request.data:
            id = ObjectId(request.data['id'])
            order = Order.objects.filter(Q(_id=id)).first()
            if order == None:
                return Response({"L'ordine non è stato trovato"})
            return Response({
                'order': serialize_order(order),
                'status': order.status,
            })
        elif 'status' in request.data:
            orders = Order.objects.filter(profile=request.user)
            return Response({
                f"{request.data['status']}_orders": orders_data(orders, request.data['status'])
            })
        else:
            return Response({
                'user_data': serialize_user(user),
                'token': str(token),
                'BTC': profile.balanceBTC,
                'USD': profile.balanceUSD,
                'profit': profit(user),
                'active_order': orders_data(orders, "active"),
                'inactive_orders': orders_data(orders, "inactive"),
                'execuded_orders': orders_data(orders, "executed"),
            })
    return Response({"Il token di autenticazione non è stato inserito o è sbagliato"})


@api_view(['GET'])
def orders(request):
    orders = Order.objects.all()
    return Response({
        "active_orders": orders_data(orders, "active")
    })


@api_view(['POST'])
def order(request):
    if 'username' in request.data and 'password' in request.data:
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
    else:
        user = request.user
    if user.is_authenticated:
        #Verifica saldo disponibile
        profile = Profile.objects.get(user=user)
        if request.data['type'] == 'buy':
            if profile.availableBalanceUSD < int(request.data['quantity']) * int(request.data['price']):
                return Response({"Il saldo USD non è disponibile"})
            else:
                profile.availableBalanceUSD -= int(request.data['quantity']) * int(request.data['price'])
        if request.data['type'] == 'sell':
            if profile.availableBalanceBTC < int(request.data['quantity']):
                return Response({"Il saldo BTC non è disponibile"})
            else:
                profile.availableBalanceBTC -= int(request.data['quantity'])
        profile.save()

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            order = serializer.save(profile=user)
            #Esegue l'ordine
            start_order(order)
            #Aggiorna i profitti
            profit(user)
            return Response({
                'order': serialize_order(order),
                'status': order.status,
            })
    return Response({"Il token di autenticazione non è stato inserito o è sbagliato"})


@api_view(['POST'])
def change_order(request):
    if 'username' in request.data and 'password' in request.data:
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
    else:
        user = request.user
    if user.is_authenticated:
        if request.data['status'] == 'inactive':
            id = ObjectId(request.data['id'])
            order = Order.objects.filter(Q(_id=id)).first()
            if order == None:
                return Response({"L'ordine non è stato trovato"})
            if order.status == "active":
                #Riaggiunta saldo disponibile
                profile = Profile.objects.get(user=user)
                if order.type == 'buy':
                    profile.availableBalanceUSD += int(order.quantityToPerformed) * int(order.price)
                    profile.save()
                if order.type == 'sell':
                    profile.availableBalanceBTC += int(order.quantityToPerformed)
                    profile.save()
                #disattivazione
                order.status = 'inactive'
                order.save()
                return Response({             
                    'order': serialize_order(order),
                    'status': order.status,
                })
            else:
                return Response({"L'ordine non può essere disattivato"})
            
        if request.data['status'] == 'active':
            id = ObjectId(request.data['id'])
            order = Order.objects.filter(Q(_id=id)).first()
            if order == None:
                return Response({"L'ordine non è stato trovato"})  
            if order.status == "inactive":
                #Verifica saldo disponibile
                profile = Profile.objects.get(user=user)
                if order.type == 'buy':
                    if profile.availableBalanceUSD < int(order.quantityToPerformed) * int(order.price):
                        return Response({"Il saldo USD non è disponibile"})
                    else:
                        profile.availableBalanceUSD -= int(order.quantityToPerformed) * int(order.price)
                        profile.save()
                if order.type == 'sell':
                    if profile.availableBalanceBTC < int(order.quantityToPerformed):
                        return Response({"Il saldo BTC non è disponibile"})
                    else:
                        profile.availabl
                        eBalanceBTC -= int(order.quantityToPerformed)
                        profile.save()

                #attivazione
                order.status = 'active'
                order.save()
                #Esegue l'ordine
                start_order(order)
                #Aggiorna i profitti
                profit(user)
                return Response({                
                    'order': serialize_order(order),
                    'status': order.status,
                })
            else:
                return Response({"L'ordine non può essere attivato"})
    return Response({"Il token di autenticazione non è stato inserito o è sbagliato"})



def serialize_user(user):
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

def serialize_order(order):
    return {
        'id': str(order._id),
        'datetime': order.datetime.strftime('%Y/%m/%d - %H:%M'),
        'type_order': order.type,
        'asset': order.currency,
        'price': order.price,
        'quantity': order.quantity,
        'quantity_to_performed': order.quantityToPerformed,
        'total_price_executed': order.totalPriceExecuted,
    }

def orders_data(orders, status):
    ordersData = []
    if status == "active":
        for order in orders:
            if order.status == "active":
                ordersData.append(serialize_order(order))
    elif status == "inactive":
        for order in orders:
            if order.status == "inactive":
                ordersData.append(serialize_order(order))
    elif status == "executed":
        for order in orders:
            if order.status == "executed":
                ordersData.append(serialize_order(order))
    return ordersData

def profit(user):
    profile = Profile.objects.get(user=user)
    orders = Order.objects.filter(profile=user)
    profile.profit = 0
    for order in orders:
        if order.status == "executed" and order.type == "sell":
            profile.profit += order.price * order.quantity
        if order.status == "executed" and order.type == "buy":
            profile.profit -= order.price * order.quantity
    profile.save()
    return profile.profit
