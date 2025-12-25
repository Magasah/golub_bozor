"""
Django management command to assign roles to staff members
Based on phone numbers (usernames)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Assign roles to staff members based on phone numbers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔐 Starting role assignment...'))
        
        # ==================== MAIN ADMIN (Superuser) ====================
        admin_email = 'muhammadrlx777@gmail.com'
        admin_username = 'muhammadrlx777'
        default_password = 'admin123'
        
        try:
            admin = User.objects.get(email=admin_email)
            self.stdout.write(f'✅ Main Admin account found: {admin_email}')
        except User.DoesNotExist:
            self.stdout.write(f'⚠️  Main Admin account not found. Creating...')
            admin = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=default_password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Main Admin account created: {admin_email}'))
            self.stdout.write(self.style.WARNING(f'📝 Default password: {default_password}'))
        
        # Set Main Admin privileges
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'👑 MAIN ADMIN ACCESS GRANTED: {admin.username}\n'
                f'   Email: {admin_email}\n'
                f'   - Superuser: ✅\n'
                f'   - Staff: ✅\n'
                f'   - Full system access'
            )
        )
        
        # ==================== MODERATOR (Staff) ====================
        moderator_email = 'spartanecsparta91@gmail.com'
        moderator_username = 'spartanec'
        
        try:
            moderator = User.objects.filter(email=moderator_email).first()
            if not moderator:
                raise User.DoesNotExist
            self.stdout.write(f'✅ Moderator account found: {moderator_email}')
        except User.DoesNotExist:
            self.stdout.write(f'⚠️  Moderator account not found. Creating...')
            moderator = User.objects.create_user(
                username=moderator_username,
                email=moderator_email,
                password=default_password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Moderator account created: {moderator_email}'))
            self.stdout.write(self.style.WARNING(f'📝 Default password: {default_password}'))
        
        # Set Moderator privileges (staff only, not superuser)
        moderator.is_superuser = False
        moderator.is_staff = True
        moderator.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🛡️  MODERATOR ACCESS GRANTED: {moderator.username}\n'
                f'   Email: {moderator_email}\n'
                f'   - Superuser: ❌\n'
                f'   - Staff: ✅\n'
                f'   - Limited admin access'
            )
        )
        
        # ==================== LEGACY PHONE USERS (Keep existing) ====================
        # Boss by phone
        boss_username = '7828162060'
        try:
            boss = User.objects.get(username=boss_username)
            boss.is_superuser = True
            boss.is_staff = True
            boss.save()
            self.stdout.write(f'✅ Legacy Boss account updated: {boss_username}')
        except User.DoesNotExist:
            pass
        
        # Moderator by phone
        mod_username = '7679557111'
        try:
            mod = User.objects.get(username=mod_username)
            mod.is_superuser = False
            mod.is_staff = True
            mod.save()
            self.stdout.write(f'✅ Legacy Moderator account updated: {mod_username}')
        except User.DoesNotExist:
            pass
        
        # ==================== SUMMARY ====================
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Role assignment completed!'))
        self.stdout.write('='*60)
        self.stdout.write(f'\n👑 Main Admin: {admin.username} ({admin_email})')
        self.stdout.write(f'🛡️  Moderator: {moderator.username} ({moderator_email})')
        self.stdout.write(f'\n📌 Login URL: /login/')
        self.stdout.write(f'📌 Dashboard URL: /dashboard/')
        self.stdout.write(f'📌 Django Admin: /control_panel_secret_7828/')
        self.stdout.write(f'📌 Telegram Bot: /admin command')
        
        if User.objects.filter(username__in=[boss_username, moderator_username]).exclude(
            password__startswith='pbkdf2_'
        ).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  SECURITY WARNING: Change default passwords!\n'
                    f'   Default password: {default_password}'
                )
            )
