from django.contrib import admin

from .models import Order, OrderItem, Transaction


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'paid', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('paid',)
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'course', 'quantity', 'price')
    search_fields = ('course__title', 'order__user__username')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider', 'amount', 'status', 'created_at')
    search_fields = ('provider_payment_id', 'order__user__username')
    list_filter = ('status', 'provider')
    ordering = ('-created_at',)
