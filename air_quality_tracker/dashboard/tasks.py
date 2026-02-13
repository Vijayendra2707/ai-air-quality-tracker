from celery import shared_task
from django.core.mail import send_mail
from .models import AQIHistory, AlertSetting

@shared_task
def check_alerts():
    latest = AQIHistory.objects.last()

    if not latest:
        return

    for alert in AlertSetting.objects.all():
        if latest.aqi > alert.threshold:
            send_mail(
                "AQI Alert",
                "Air quality is unhealthy. Avoid outdoor activity.",
                None,
                [alert.user.email]
            )
