from django.core.management.base import BaseCommand
from contact.models import ContactSupportChannel, PopularQuestion


class Command(BaseCommand):
    help = 'Seeds initial Contact Us support channels and popular questions based on app design.'

    def handle(self, *args, **options):
        # 1. Support Channels
        channels = [
            {
                'channel_type': 'live_chat',
                'title': 'Live Chat',
                'subtitle': '2 min response',
                'value': 'https://baoiam.com/live-chat',
                'display_order': 1,
            },
            {
                'channel_type': 'call',
                'title': 'Call Us',
                'subtitle': '24/7 support',
                'value': '+91-8000000000',
                'display_order': 2,
            },
            {
                'channel_type': 'email',
                'title': 'Email',
                'subtitle': '4 hr response',
                'value': 'support@baoiam.com',
                'display_order': 3,
            },
        ]

        for item in channels:
            obj, created = ContactSupportChannel.objects.update_or_create(
                channel_type=item['channel_type'],
                defaults=item,
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"{action} channel: {obj.title}"))

        # 2. Popular Questions
        questions = [
            {
                'question': 'How to reset password?',
                'answer': 'Go to the Login screen, click on "Forgot Password", enter your registered email address, and verify the OTP sent to your inbox to set a new password.',
                'category': 'Account',
                'display_order': 1,
            },
            {
                'question': 'Cancel subscription',
                'answer': 'To manage or cancel your active subscription, open Profile -> Manage Subscription -> Cancel Plan, or reach out to support.',
                'category': 'Billing',
                'display_order': 2,
            },
            {
                'question': 'Payment methods',
                'answer': 'We accept UPI (GPay, PhonePe, Paytm), Credit & Debit Cards (Visa, MasterCard, RuPay), and Net Banking.',
                'category': 'Payment',
                'display_order': 3,
            },
            {
                'question': 'Technical issues',
                'answer': 'Check your internet connection and make sure your app is updated. If the issue persists, submit a message via the form above.',
                'category': 'Technical',
                'display_order': 4,
            },
        ]

        for q in questions:
            obj, created = PopularQuestion.objects.update_or_create(
                question=q['question'],
                defaults=q,
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"{action} popular question: {obj.question}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Contact Us data.'))
