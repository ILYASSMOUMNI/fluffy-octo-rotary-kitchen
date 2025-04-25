from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class ChefApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivation = models.TextField()
    experience = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_applications'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Chef Application by {self.user.username}"

    class Meta:
        ordering = ['-created_at']

class ChefBadge(models.Model):
    BADGE_TYPES = [
        ('beginner', 'Beginner Chef'),
        ('intermediate', 'Intermediate Chef'),
        ('expert', 'Expert Chef'),
        ('master', 'Master Chef'),
    ]
    
    chef = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    awarded_at = models.DateTimeField(default=timezone.now)
    awarded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='awarded_badges'
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_badge_type_display()} - {self.chef.username}"

    class Meta:
        ordering = ['-awarded_at']
