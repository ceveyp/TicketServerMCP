from typing import Literal

Priorities = Literal['P1', 'P2', 'P3', 'P4']

SortDirections = Literal['ASC', 'DESC']

Departments = Literal[
    'operations',
    'sales',
    'marketing',
    'it',
    'merchandising',
    'accounting',
    'screen_print',
    'art'
]

Statuses = Literal[
    'open',
    'in_progress',
    'waiting',
    'closed'
]

TicketTypes = Literal[
    'generic',
    'linesheet_update',
    'credit_memo',
    'order_modification',
    'rma_request',
    'payroll_discrepancy',
    'recruiting_request',
    'po_item_inquiry',
    'accounting_close',
    'customer_billing_inquiry',
    'system_access_request'
]
