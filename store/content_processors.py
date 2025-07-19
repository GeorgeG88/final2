from .models import Cart

def cart_count(request):
    try:
        cart = Cart.objects.get(id=request.session.get('cart_id'))
        count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return {'cart_count': count}
    except Cart.DoesNotExist:
        return {'cart_count': 0}