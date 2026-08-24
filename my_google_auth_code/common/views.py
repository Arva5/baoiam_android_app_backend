from django.shortcuts import render


def google_test_page(request):
    """Simple browser page to test /api/auth/google/signup/ and
    /api/auth/google/login/ without needing the Android app yet."""
    return render(request, "common/google_test.html")
