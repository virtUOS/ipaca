from django.conf import settings


def cheating(request):
    return {'CHEAT': settings.CHEAT}

