from django.core.management.base import BaseCommand

from legal.models import LegalDocument


class Command(BaseCommand):
    """
    One-time helper to create a starting Terms & Conditions and Privacy
    Policy document, using the text from the app's current hardcoded
    screen, so the API has something to return immediately.

    Run:  python manage.py seed_legal_docs
    After this, edit the content anytime from /admin/ - no code change
    needed, and the app will pick it up automatically via GET /api/legal/terms/.
    """

    help = "Seeds an initial Terms & Conditions and Privacy Policy document."

    def handle(self, *args, **options):
        terms_content = (
            "1. User Responsibilities\n"
            "- Maintain accurate and up-to-date account information\n"
            "- Ensure secure password protection and account confidentiality\n"
            "- Comply with all applicable laws and regulations while using our services\n\n"
            "2. Payment & Refund Policy\n"
            "All payments are processed securely through our authorized payment "
            "partners. Course fees are non-refundable after the first 7 days of "
            "purchase. Refund requests within the first 7 days will be processed "
            "within 5-7 business days.\n\n"
            "3. Code of Conduct\n"
            "- Respect intellectual property rights and copyright laws\n"
            "- Maintain professional conduct during live classes\n"
            "- No harassment or inappropriate behavior towards others\n\n"
            "4. Intellectual Property Rights\n"
            "All content provided on this platform is protected by copyright "
            "laws. Users may not reproduce, distribute, or create derivative "
            "works without explicit permission.\n\n"
            "5. Privacy & Data Protection\n"
            "We collect and process personal data in accordance with our "
            "Privacy Policy. By using our services, you consent to our data "
            "practices.\n\n"
            "6. Dispute Resolution\n"
            "Any disputes arising from the use of our services will be resolved "
            "through arbitration in accordance with applicable laws."
        )

        terms, created = LegalDocument.objects.get_or_create(
            doc_type="terms",
            version="1.0",
            defaults={
                "title": "Terms & Conditions",
                "content": terms_content,
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Already exists'}: {terms}"
        ))

        privacy, created = LegalDocument.objects.get_or_create(
            doc_type="privacy",
            version="1.0",
            defaults={
                "title": "Privacy Policy",
                "content": "Add your Privacy Policy text here (edit from /admin/).",
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Already exists'}: {privacy}"
        ))
