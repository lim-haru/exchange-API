from .models import Profile, Order

def start_order(order):
    if order.type == "buy":
        seller = Order.objects.filter(status="active", type="sell", price__lte=order.price).exclude(profile=order.profile).order_by('-price').first()        
        if seller:
            profileSeller = Profile.objects.get(user=seller.profile)
            profileBuyer = Profile.objects.get(user=order.profile)

            if order.quantityToPerformed - seller.quantityToPerformed <= 0:
                #Calcolo costo ordini
                cost = order.quantityToPerformed * seller.price
                #Modifica saldo BTC buyer
                profileBuyer.balanceBTC += order.quantityToPerformed
                profileBuyer.availableBalanceBTC += order.quantityToPerformed
                #Modifica lo stato dell'ordine
                order.status = "executed"
            else:
                #Calcolo costo ordini
                cost = seller.quantityToPerformed * seller.price
                #Modifica saldo BTC buyer
                profileBuyer.balanceBTC += seller.quantityToPerformed
                profileBuyer.availableBalanceBTC += seller.quantityToPerformed
                #Modifica la quantità da eseguire rimanente
                order.quantityToPerformed -= seller.quantityToPerformed


            if seller.quantityToPerformed - order.quantityToPerformed <= 0:
                #Modifica saldo BTC seller
                profileSeller.balanceBTC -= seller.quantityToPerformed
                #Modifica lo stato dell'ordine
                seller.status = "executed"
            else:
                #Modifica saldo BTC seller
                profileSeller.balanceBTC -= order.quantityToPerformed
                #Modifica la quantità da eseguire rimanente
                seller.quantityToPerformed -= order.quantityToPerformed

            #Modifica saldo USD seller
            profileSeller.balanceUSD += cost
            profileSeller.availableBalanceUSD += cost
            #Modifica saldo USD buyer
            profileBuyer.balanceUSD -= cost

            #Aggiunta differenza prezzo ordine e prezzo eseguito
            profileBuyer.availableBalanceUSD += order.price - seller.price
            #Modifica la quantità da eseguire
            if order.status == "executed":
                order.quantityToPerformed = 0
            #Modifica la quantità da eseguire
            if seller.status == "executed":
                seller.quantityToPerformed = 0
            #Prezzo totale reale di acquisto
            order.totalPriceExecuted += cost
            #Prezzo totale di vendita
            seller.totalPriceExecuted += cost
            
            # #Aggiorna i profitti
            # orders = Order.objects.filter(profile=order.profile)
            # profit(profileBuyer, orders)

            seller.save()
            order.save()
            profileSeller.save()
            profileBuyer.save()
            return


    if order.type == "sell":
        buyer = Order.objects.filter(status="active", type="buy", price__gte=order.price).exclude(profile=order.profile).order_by('price').first()        
        if buyer:
            profileBuyer = Profile.objects.get(user=buyer.profile)
            profileSeller = Profile.objects.get(user=order.profile)


            if order.quantityToPerformed - buyer.quantityToPerformed <= 0:
                #Calcolo costo ordini
                cost = order.quantityToPerformed * order.price
                #Modifica saldo BTC buyer
                profileBuyer.balanceBTC += order.quantityToPerformed
                profileBuyer.availableBalanceBTC += order.quantityToPerformed
                #Modifica lo stato dell'ordine
                order.status = "executed"
            else:
                #Calcolo costo ordini
                cost = buyer.quantityToPerformed * order.price
                #Modifica saldo BTC buyer
                profileBuyer.balanceBTC += buyer.quantityToPerformed
                profileBuyer.availableBalanceBTC += buyer.quantityToPerformed
                #Modifica la quantità da eseguire rimanente
                order.quantityToPerformed -= buyer.quantityToPerformed


            if buyer.quantityToPerformed - order.quantityToPerformed <= 0:
                #Modifica saldo BTC buyer
                profileSeller.balanceBTC -= buyer.quantityToPerformed
                #Modifica lo stato dell'ordine
                buyer.status = "executed"
            else:
                #Modifica saldo BTC buyer
                profileSeller.balanceBTC -= order.quantityToPerformed
                #Modifica la quantità da eseguire rimanente
                buyer.quantityToPerformed -= order.quantityToPerformed
                
            #Modifica saldo USD buyer
            profileSeller.balanceUSD += cost
            profileSeller.availableBalanceUSD += cost
            #Modifica saldo USD buyer
            profileBuyer.balanceUSD -= cost

            #Aggiunta differenza prezzo ordine e prezzo eseguito
            profileBuyer.availableBalanceUSD += buyer.price - order.price

            #Modifica la quantità da eseguire
            if order.status == "executed":
                order.quantityToPerformed = 0
            #Modifica la quantità da eseguire
            if buyer.status == "executed":
                buyer.quantityToPerformed = 0

            #Prezzo totale reale di acquisto
            buyer.totalPriceExecuted += cost
            #Prezzo totale di vendita
            order.totalPriceExecuted += cost

            # #Aggiorna i profitti
            # orders = Order.objects.filter(profile=order.profile)
            # profit(profileSeller, orders)

            buyer.save()
            order.save()
            profileSeller.save()
            profileBuyer.save()
            return
