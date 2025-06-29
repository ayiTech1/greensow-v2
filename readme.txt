#pip freeze > requirements.txt

from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Every 5 minutes
schedule, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)

# Auto Start Task
PeriodicTask.objects.update_or_create(
    name="Auto Start Shifts",
    defaults={
        'interval': schedule,
        'task': 'shift.tasks.auto_start_shifts'
    }
)

# Auto Complete Task
PeriodicTask.objects.update_or_create(
    name="Auto Complete Shifts",
    defaults={
        'interval': schedule,
        'task': 'shift.tasks.auto_complete_shifts'
    }
)

docker-compose down -v
docker-compose up --build
