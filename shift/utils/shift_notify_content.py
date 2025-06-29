from shift.models.shift import Shift


def build_shift_notification_content(action: str, shift: Shift, employee_email: str = None) -> tuple[str, str, str]:
    """
    Returns (message, title, status) for a given shift action.
    If employee_email is provided, it is included in the message.
    """
    employer_email = shift.employer.email if shift.employer else "an employer"

    if action == "created_by_manager":
        return (
            f"A new shift '{shift.name}' at {shift.company_name} has been created by your manager.",
            "Shift Created by Manager",
            "created"
        )
    elif action == "deleted_by_manager":
        return (
            f"Your shift '{shift.name}' at {shift.company_name} has been deleted by the manager.",
            "Shift Deleted",
            "deleted"
        )
    elif action == "deleted_by_employer" and shift.manager:
        return (
            f"The shift '{shift.name}' at {shift.company_name} created by {employer_email} has been deleted by the employer.",
            "Shift Deleted",
            "deleted"
        )
    elif action == "updated_by_employer" and shift.manager:
        return (
            f"The shift '{shift.name}' at {shift.company_name} was updated by {employer_email} and may require re-approval.",
            "Shift Updated by Employer",
            "pending_update"
        )
    elif action == "pending_approval":
        return (
            f"A new shift '{shift.name}' at {shift.company_name} has been created by {employer_email} and needs your approval.",
            "New Shift Pending Approval",
            "pending_approval"
        )
    elif action == "approved":
        return (
            f"Your shift '{shift.name}' at {shift.company_name} has been approved by the manager.",
            "Shift Approved",
            "approved"
        )
    elif action == "rejected":
        return (
            f"Your shift '{shift.name}' at {shift.company_name} has been rejected by the manager.",
            "Shift Rejected",
            "rejected"
        )
    # Employee-related notifications:
    elif action == "taken":
        return (
            f"Employee {employee_email} has taken the shift '{shift.name}' at {shift.company_name}.",
            "Shift Taken",
            "taken"
        )
    elif action == "started":
        return (
            f"Employee {employee_email} has started the shift '{shift.name}' at {shift.company_name}.",
            "Shift Started",
            "started"
        )
    elif action == "cancelled":
        return (
            f"Employee {employee_email} has cancelled the shift '{shift.name}' at {shift.company_name}.",
            "Shift Cancelled",
            "cancelled"
        )
    elif action == "completed":
        return (
            f"Employee {employee_email} has completed the shift '{shift.name}' at {shift.company_name}.",
            "Shift Completed",
            "completed"
        )
    return "", "", ""
