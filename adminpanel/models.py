from django.db import models
from users.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    can_approve_chefs = models.BooleanField(default=True)
    is_super_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Admin: {self.user.username}"

