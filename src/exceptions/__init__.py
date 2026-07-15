"""Custom exception package for the Freelance Project Manager."""

from .app_exceptions import (
    ApplicationException,
    BudgetExceededException,
    DeadlinePassedException,
    InvalidTaskException,
    InvoiceAlreadyPaidException,
    ClientNotFoundException,
    InvalidBillingStrategyException,
    ProfileNotFoundException,
    DuplicateInvoiceException,
)

__all__ = [
    "ApplicationException",
    "BudgetExceededException",
    "DeadlinePassedException",
    "InvalidTaskException",
    "InvoiceAlreadyPaidException",
    "ClientNotFoundException",
    "InvalidBillingStrategyException",
    "ProfileNotFoundException",
    "DuplicateInvoiceException",
]
