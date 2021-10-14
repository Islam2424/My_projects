from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
#from django.urls import reverse


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'],)
            # Очищаем корзину.
            cart.clear()
            # Запускаем асинхронную задачу
            order_created.delay(order.id)
            return render(request,
                          'orders/order/created.html',
                          {'order': order})
            # Сохраняю заказ в сессии
            # reverse.session['order_id'] = order.id
            # Перенапрявляю на страницу оплаты
            # return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
            'orders/order/create.html',
            {'cart': cart, 'form': form})
