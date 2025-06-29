


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.models.notification import Notification
from accounts.models.user import User
from shift.models import Shift
from shift.models.assignment import ShiftAssignment
from shift.utils.shift_notify_content import build_shift_notification_content


def notify_user_shift(user_id, shift: Shift, status: str, message: str, title: str = None):
    """
    Sends a shift-related notification to a user (via DB and WebSocket).
    """
    user = User.objects.get(pk=user_id)

    # Create DB notification
    notification = Notification.objects.create(
        recipient=user,
        title=title or f"Shift {status.capitalize()}",
        message=message,
        status=status
    )

    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",  
        {
            "type": "user.status",
            "status": status,
            "message": message,
            "notification_id": notification.id,
            "title": notification.title,
            "timestamp": str(notification.timestamp),
        }
    )





def notify_managers_about_shift(shift: Shift):
    """
    Notify all managers that a new shift was created and needs approval.
    """
    managers = User.objects.filter(role__name='manager')
    message, title, status = build_shift_notification_content("pending_approval", shift)

    for manager in managers:
        notify_user_shift(user_id=manager.id, shift=shift, status=status, message=message,title=title)


def notify_employer_shift_status(shift: Shift, approved=True):
    """
    Notifies the employer that their shift has been approved or rejected.
    """
    action = "approved" if approved else "rejected"
    message, title, status = build_shift_notification_content(action, shift)

    notify_user_shift(user_id=shift.employer.id, shift=shift, status=status, message=message, title=title)


def notify_employer_shift_created_by_manager(shift: Shift):
    """
    Notify employer that a manager has created a shift for them.
    """
    message, title, status = build_shift_notification_content("created_by_manager", shift)
    notify_user_shift(shift.employer.id, shift, status, message, title)


def notify_employer_shift_deleted_by_manager(shift: Shift):
    """
    Notify the employer that their shift has been deleted by the manager.
    """
    message, title, status = build_shift_notification_content("deleted_by_manager", shift)
    notify_user_shift(shift.employer.id, shift, status, message, title)


def notify_manager_shift_deleted_by_employer(shift: Shift):
    """
    Notify the assigned manager that a shift was deleted by the employer.
    """
    if not shift.manager:
        return
    message, title, status = build_shift_notification_content("deleted_by_employer", shift)
    notify_user_shift(shift.manager.id, shift, status, message, title)


def notify_manager_shift_updated_by_employer(shift: Shift):
    """
    Notify the assigned manager that a shift was updated by the employer and may need re-approval.
    """
    if not shift.manager:
        return
    message, title, status = build_shift_notification_content("updated_by_employer", shift)
    notify_user_shift(shift.manager.id, shift, status, message, title)


def notify_shift_started(assignment: ShiftAssignment):
    """
    Notify employer and manager that employee has started the shift.
    """
    shift = assignment.shift
    employee_email = assignment.employee.email

    message, title, status = build_shift_notification_content("started", shift, employee_email)

    if shift.employer:
        notify_user_shift(
            user_id=shift.employer.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

    if shift.manager:
        notify_user_shift(
            user_id=shift.manager.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )


def notify_shift_cancelled(assignment: ShiftAssignment):
    """
    Notify employer and manager that employee has cancelled the shift.
    """
    shift = assignment.shift
    employee_email = assignment.employee.email

    message, title, status = build_shift_notification_content("cancelled", shift, employee_email)

    if shift.employer:
        notify_user_shift(
            user_id=shift.employer.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

    if shift.manager:
        notify_user_shift(
            user_id=shift.manager.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )


def notify_shift_completed(assignment: ShiftAssignment):
    """
    Notify employer and manager that employee has completed the shift.
    """
    shift = assignment.shift
    employee_email = assignment.employee.email

    message, title, status = build_shift_notification_content("completed", shift, employee_email)

    if shift.employer:
        notify_user_shift(
            user_id=shift.employer.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

    if shift.manager:
        notify_user_shift(
            user_id=shift.manager.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

def notify_shift_taken(assignment: ShiftAssignment):
    """
    Notify employer and manager that employee has taken the shift.
    """
    shift = assignment.shift
    employee_email = assignment.employee.email

    message, title, status = build_shift_notification_content("taken", shift, employee_email)

    if shift.employer:
        notify_user_shift(
            user_id=shift.employer.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

    if shift.manager:
        notify_user_shift(
            user_id=shift.manager.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )


    message, title, status = build_shift_notification_content("completed", shift, employee_email)

    if shift.employer:
        notify_user_shift(
            user_id=shift.employer.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )

    if shift.manager:
        notify_user_shift(
            user_id=shift.manager.id,
            shift=shift,
            status=status,
            message=message,
            title=title
        )