from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates an admin user'

    def handle(self, *args, **options):
        try:
            User = get_user_model()
            if not User.objects.filter(username=settings.ADMIN_USERNAME).exists():
                user = User.objects.create_user(
                    username=settings.ADMIN_USERNAME,
                    email=settings.ADMIN_EMAIL,
                    password=settings.ADMIN_PASSWORD,
                    role='admin'
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
            else:
                self.stdout.write(self.style.WARNING('Admin user already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}')) 