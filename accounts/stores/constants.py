APPROVAL_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
]

ROLE_CHOICES = [
    ('manager', 'Manager'),
    ('employer', 'Employer'),
    ('employee', 'Employee')
]

PURPOSE_CHOICES = [
        ('account_verification', 'Account Verification'),
        ('password_reset', 'Password Reset'),
    ]



OTP_PURPOSE_ACCOUNT_VERIFICATION = 'account_verification'
OTP_PURPOSE_PASSWORD_RESET = 'password_reset'


# ============== Profile Message =================

PROFILE_APPROVED_SUBJECT = "Profile Approved"
PROFILE_APPROVED_MESSAGE = "Your profile has been approved."

PROFILE_REJECTED_SUBJECT = "Profile Rejected"
PROFILE_REJECTED_MESSAGE = "Your profile has been rejected."


