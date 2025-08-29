import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger("auth")
User = get_user_model()


class Command(BaseCommand):
    help = "Deletes unactivated user accounts that have expired"

    def handle(self, *args, **options):
        expiration_period = timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        expiration_threshold = timezone.now() - expiration_period

        expired_users = User.objects.filter(
            is_active=False, date_joined__lt=expiration_threshold
        )
        deleted_count = 0

        for user in expired_users:
            try:
                logger.info("Deleting expired user account: %s", user.email)
                user.delete()
                deleted_count += 1
            except Exception as e:  # pylint: disable=W0718
                logger.error("Error deleting user %s: %s", user.email, e)

        self.stdout.write(f"Successfully deleted {deleted_count} expired user(s)")
