import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from products.models import Product

from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem

"""retrieve stripe api key from environment variables"""
stripe.api_key = settings.STRIPE_SECRET


"""
checkout function. orderform and paymentform are
displayed together so user can check out with one form.
"""
def checkout(request):
    if request.user.is_anonymous:
        messages.add_message(request, messages.INFO,
                             'You must be logged in to check out.')
        return redirect('login')
    else:
        if request.method == "POST":
            order_form = OrderForm(request.POST)
            payment_form = MakePaymentForm(request.POST)

            """check if both orderform and paymentform are valid"""
            if order_form.is_valid() and payment_form.is_valid():

                """save orderform information"""
                order = order_form.save(commit=False)
                order.date = timezone.now()
                order.save()

                """Get all neccessary information from the cart."""
                cart = request.session.get('cart', {})
                total = 0
                for id, quantity in cart.items():
                    product = get_object_or_404(Product, pk=id)
                    total += quantity * product.price
                    order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    )
                    order_line_item.save()

                """using stripe for payment"""
                try:
                    customer = stripe.Charge.create(
                        amount=int(total*100),
                        currency="EUR",
                        description=request.user.email,
                        card=payment_form.cleaned_data['stripe_id'],
                    )
                except stripe.error.CardError:
                    messages.error(request, "Your card was declined.")

                if customer.paid:
                    messages.error(request, "The payment was successfull.")
                    request.session['cart'] = {}
                    return redirect(reverse('confirmation'))

                else:
                    messages.error(request, "Unable to process payment.")

            else:
                messages.error(request, "Unable to take payment with this card.")
                
        else:
            order_form = OrderForm()
            payment_form = MakePaymentForm()

        return render(request, "checkout.html", {
                                                'order_form': order_form,
                                                'payment_form': payment_form,
                                                'publishable': settings.STRIPE_PUBLISHABLE,
                                                })

def confirmation(request):
    """return confirmation.html"""

    return render(request,
                'confirmation.html')
