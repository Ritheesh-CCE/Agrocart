import json
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from .cart import Cart
from .forms import OrderForm
from . models import Product,Category,Order,OrderItem

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('cart_view')

def change_quantity(request,product_id):
    action = request.GET.get('action', '')

    if action:
        quantity=1

        if action == 'decrease':
            quantity=-1

        cart = Cart(request)
        cart.add(product_id,quantity,True)
    
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart_view')


def cart_view(request):
    cart = Cart(request)

    return render(request, 'store/cart_view.html',{
        'cart': cart
    })

@login_required
def checkout(request):
    cart = Cart(request)
    #data = json.loads(request.body)
    if request.method == 'POST':

        form = OrderForm(request.POST)

        
        total_price = 0
        items = []
        for item in cart:
            product = item['product']
            total_price += product.price * int(item['quantity'])
            items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': product.title,
                    },
                    'unit_amount': product.price
                },
                'quantity': item['quantity']
            })

        print('items',items)

        '''stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=items,
            mode='payment',
            success_url='http://127.0.0.1:8000/cart/success/',
            cancel_url='http://127.0.0.1:8000/cart/',
        )
        payment_intent = session.payment_intent

        print('data', data['first_name'])
            
        order = form.save(commit=False)
        order.first_name = data['first_name']
        order.last_name = data['last_name']
        order.address = data['address']
        order.zipcode = data['zipcode']
        order.city = data['city']
        order.created_by = request.user
        order.is_paid = True
        order.payment_intent = payment_intent
        order.paid_amount = total_price
        order.save()

        for item in cart:
            product = item['product']
            quantity = int(item['quantity'])
            price = product.price * quantity

            item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
            
        cart.clear()

        return JsonResponse({'session': session, 'order': payment_intent})'''
        return ('frontpage')

    else:
        form = OrderForm()
    return render(request, 'store/checkout.html',{
        'cart':cart,
        'form':form,
        'pub_key':settings.STRIPE_PUB_KEY,
    })

def search(request):
    query=request.GET.get('query', '')
    products = Product.objects.filter(status=Product.ACTIVE).filter(
        Q(title__icontains=query)
        |
        Q(description__icontains=query))

    return render(request,'store/search.html',{
        'query': query,
        'products' : products,
        
    })

def category_detail(request,slug):
    category=get_object_or_404(Category,slug=slug,)
    products=category.products.filter(status=Product.ACTIVE)
    return render(request,'store/category_detail.html',{
        'category':category,
        'products':products 
        })

def product_detail(request,category_slug,slug):
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE)
    return render(request,'store/product_detail.html',{'product':product})
