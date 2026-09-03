from django.shortcuts import render


def google_test_page(request):
    """Simple browser page to test /api/auth/google/ (unified signup+login)
    without needing the Android app yet."""
    return render(request, "common/google_test.html")
