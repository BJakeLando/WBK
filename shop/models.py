from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Product(models.Model):
    """Represents a painting/print available for purchase"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Categorization
    CATEGORY_CHOICES = [
        ('wedding', 'Wedding'),
        ('landscape', 'Landscape'),
        ('portrait', 'Portrait'),
        ('abstract', 'Abstract'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-created_at']
    
    def __str__(self):
        return self.name


class PrintSize(models.Model):
    """Available print sizes and prices for a product"""
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    
    SIZE_CHOICES = [
        ('5x7', '5" × 7"'),
        ('8x10', '8" × 10"'),
        ('11x14', '11" × 14"'),
        ('16x20', '16" × 20"'),
        ('18x24', '18" × 24"'),
        ('24x36', '24" × 36"'),
    ]
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['price']
        unique_together = ['product', 'size']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()} (${self.price})"


class Cart(models.Model):
    """Shopping cart - supports both guest and logged-in users"""
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart ({self.session_key[:8]}...)"
    
    def get_total(self):
        """Calculate total cart value"""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a shopping cart"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    print_size = models.ForeignKey(PrintSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'print_size']
    
    def __str__(self):
        return f"{self.quantity}x {self.print_size}"
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.print_size.price * self.quantity


class Order(models.Model):
    """Customer orders"""
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Customer info (supports guest checkout)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    
    # Shipping address
    address = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='US')
    
    # Payment ID
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            self.order_number = f"WBK{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_shipping_address(self):
        """Return formatted shipping address"""
        address_parts = [
            self.address,
            self.address_line_2,
            f"{self.city}, {self.state} {self.zip_code}",
            self.country
        ]
        return '\n'.join([part for part in address_parts if part])


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # Store product details at time of purchase (in case product changes later)
    product_name = models.CharField(max_length=255)
    size = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size})"
    
    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price * self.quantity