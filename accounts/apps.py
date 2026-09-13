from django.apps import AppConfig
from django.db.models.signals import post_migrate


def auto_create_admin(sender, **kwargs):
    if sender.name == 'accounts':
        import os
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'bao.iam.st2020@gmail.com')
        admin_password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'Admin@Baoiam2026')

        if not User.objects.filter(is_staff=True).exists():
            user, created = User.objects.get_or_create(
                email=admin_email,
                defaults={
                    'name': 'Admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'email_verified': True,
                    'is_active': True,
                }
            )
            user.set_password(admin_password)
            user.is_staff = True
            user.is_superuser = True
            user.email_verified = True
            user.is_active = True
            user.save()
            print(f"[AUTO-ADMIN] Created superuser: {admin_email}")


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        post_migrate.connect(auto_create_admin, sender=self)

