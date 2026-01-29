from django.contrib import admin
from .models import Product, PrintSize, Cart, CartItem, Order, OrderItem


class PrintSizeInline(admin.TabularInline):
    model = PrintSize
    extra = 3
    fields = ['size', 'price', 'in_stock']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'featured', 'created_at']
    list_filter = ['category', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'featured']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PrintSizeInline]
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrintSize)
class PrintSizeAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'price', 'in_stock']
    list_filter = ['in_stock', 'size', 'product__category']
    search_fields = ['product__name', 'size']
    list_editable = ['price', 'in_stock']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['print_size', 'quantity', 'added_at']
    can_delete = False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'get_item_count', 'get_total', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'get_total', 'get_item_count']
    inlines = [CartItemInline]
    
    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = 'Total'
    
    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'size', 'quantity', 'price', 'get_subtotal']
    can_delete = False
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'get_full_name', 'email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'shipped_at']
    search_fields = ['order_number', 'email', 'first_name', 'last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at', 
                      'get_shipping_address', 'stripe_payment_intent']
    list_editable = ['status']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'user')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'address_line_2', 'city', 'state', 'zip_code', 'country', 
                      'get_shipping_address')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total_amount')
        }),
        ('Payment', {
            'fields': ('stripe_payment_intent',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Customer'
    
    def get_shipping_address(self, obj):
        return obj.get_shipping_address()
    get_shipping_address.short_description = 'Formatted Address'
    
    actions = ['mark_as_processing', 'mark_as_shipped']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as Processing'
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as Shipped'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'size', 'quantity', 'price', 'get_subtotal']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product_name']
    readonly_fields = ['order', 'product_name', 'size', 'quantity', 'price', 'get_subtotal']
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        return False