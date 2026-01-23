from django.contrib import admin
from .models import Product, ProductVariant, Cart, CartItem, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'is_active', 'featured', 'created_at']
    list_filter = ['category', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'description', 'printful_id']
    list_editable = ['is_active', 'featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'base_price', 'image_url')
        }),
        ('Printful Integration', {
            'fields': ('printful_id',)
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'paper_type', 'price', 'sku', 'in_stock', 'printful_variant_id']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'paper_type', 'price', 'in_stock', 'sku']
    list_filter = ['in_stock', 'paper_type', 'product__category']
    search_fields = ['product__name', 'sku', 'size']
    list_editable = ['price', 'in_stock']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variant', 'quantity', 'added_at']
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
    readonly_fields = ['product_name', 'variant_size', 'variant_paper_type', 'quantity', 'price', 'get_subtotal']
    can_delete = False
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'get_full_name', 'email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'shipped_at']
    search_fields = ['order_number', 'email', 'first_name', 'last_name', 'printful_order_id']
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
        ('Payment & Fulfillment', {
            'fields': ('stripe_payment_intent', 'printful_order_id')
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
    list_display = ['order', 'product_name', 'variant_size', 'quantity', 'price', 'get_subtotal']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product_name']
    readonly_fields = ['order', 'variant', 'product_name', 'variant_size', 'variant_paper_type', 
                      'quantity', 'price', 'get_subtotal']
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        return False