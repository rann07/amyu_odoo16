BILLING_METHOD_CHOICES = [
    ('email', 'Email'),
    ('hardcopy', 'Hardcopy'),
    ('email_and_hardcopy', 'Email & Hardcopy'),
]
BILLING_METHOD_DEFAULT = 'email'

PAYMENT_METHOD_CHOICES = [
    ('online', 'Online'),
    ('check', 'Check'),
    ('cash', 'Cash'),
]
PAYMENT_METHOD_DEFAULT = 'online'

BANK_TYPES_PER_PAYMENT = {
    'cash': None,
    'online': 'online',
    'check': 'physical',
}

BANK_TYPE_DEFAULT = BANK_TYPES_PER_PAYMENT[PAYMENT_METHOD_DEFAULT]
