"""
Signals for the notifications system.
"""
from django.dispatch import Signal, receiver

# Custom signal sent when a notification is created
notification_created = Signal()


@receiver(notification_created)
def handle_notification_created(sender, notification=None, **kwargs):
    """
    Handler for notification creation. Can be used for push notifications (e.g. FCM/APNS) or metrics.
    """
    pass
