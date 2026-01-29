from django.db import models
from django.utils import timezone

class PetPortraitSubmission(models.Model):
    # Customer Information
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Pet Information
    pet_name = models.CharField(max_length=100)
    pet_photo = models.ImageField(upload_to='pet_submissions/')
    additional_notes = models.TextField(blank=True, help_text="Any special requests or details about the pet")
    
    # Order Information
    portrait_size = models.CharField(
        max_length=50,
        choices=[
            ('8x10', '8" x 10" - $150'),
            ('11x14', '11" x 14" - $200'),
            ('16x20', '16" x 20" - $300'),
        ],
        default='8x10'
    )
    
    # Payment Information
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=200, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('delivered', 'Delivered'),
        ],
        default='submitted'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pet Portrait Submission'
        verbose_name_plural = 'Pet Portrait Submissions'
    
    def __str__(self):
        return f"{self.pet_name} - {self.customer_name} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_price(self):
        """Return the price based on portrait size"""
        prices = {
            '8x10': 150.00,
            '11x14': 200.00,
            '16x20': 300.00,
        }
        return prices.get(self.portrait_size, 150.00)