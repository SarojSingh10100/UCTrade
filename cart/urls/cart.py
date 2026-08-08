from django.urls import path

from cart.views import CartViewSet

cart_list = CartViewSet.as_view({'get': 'list', 'post': 'create'})
cart_item_detail = CartViewSet.as_view({'delete': 'destroy'})
cart_checkout = CartViewSet.as_view({'post': 'checkout'})

urlpatterns = [
    path('', cart_list, name='cart'),
    path('items/<int:pk>/', cart_item_detail, name='cart-item-detail'),
    path('checkout/', cart_checkout, name='cart-checkout'),
]
