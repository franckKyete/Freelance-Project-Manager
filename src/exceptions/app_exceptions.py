"""Custom exception hierarchy for the Freelance Project Manager.

All exceptions inherit from ApplicationException, which itself inherits
from Python's built-in Exception class.

Example:
    try:
        invoice.mark_as_paid()
    except InvoiceAlreadyPaidException as e:
        print(f"Error: {e}")
    finally:
        db.commit()
"""


class ApplicationException(Exception):
    """Base exception for all application-level errors.

    Args:
        message: Human-readable description of the error.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class BudgetExceededException(ApplicationException):
    """Raised when a project expense or invoice amount exceeds the budget.

    Args:
        message: Description including the exceeded amount if available.
    """

    def __init__(self, message: str = "Project budget has been exceeded.") -> None:
        super().__init__(message)


class DeadlinePassedException(ApplicationException):
    """Raised when a supplied date is in the past where a future date is required.

    Args:
        message: Description including the offending date if available.
    """

    def __init__(self, message: str = "The specified deadline has already passed.") -> None:
        super().__init__(message)


class InvalidTaskException(ApplicationException):
    """Raised when task data fails validation.

    Args:
        message: Specific validation error description.
    """

    def __init__(self, message: str = "Invalid task data provided.") -> None:
        super().__init__(message)


class InvoiceAlreadyPaidException(ApplicationException):
    """Raised when attempting to pay an invoice that is already marked as paid.

    Args:
        invoice_number: The number of the already-paid invoice.
    """

    def __init__(self, invoice_number: str = "") -> None:
        msg = f"Invoice '{invoice_number}' has already been paid." if invoice_number else "Invoice is already paid."
        super().__init__(msg)


class ClientNotFoundException(ApplicationException):
    """Raised when a client cannot be found in the system.

    Args:
        client_id: The ID that was searched for.
    """

    def __init__(self, client_id: int = 0) -> None:
        msg = f"Client with id={client_id} was not found." if client_id else "Client not found."
        super().__init__(msg)


class InvalidBillingStrategyException(ApplicationException):
    """Raised when an unrecognised billing strategy type is specified.

    Args:
        strategy_name: The name of the invalid strategy.
    """

    def __init__(self, strategy_name: str = "") -> None:
        msg = (
            f"'{strategy_name}' is not a valid billing strategy."
            if strategy_name
            else "Invalid billing strategy."
        )
        super().__init__(msg)


class ProfileNotFoundException(ApplicationException):
    """Raised when the freelancer profile record does not exist in the database.

    This normally triggers the first-run setup wizard.
    """

    def __init__(self, message: str = "No freelancer profile found. Please complete setup.") -> None:
        super().__init__(message)


class DuplicateInvoiceException(ApplicationException):
    """Raised when attempting to create an invoice with an already-existing invoice number.

    Args:
        invoice_number: The duplicate invoice number.
    """

    def __init__(self, invoice_number: str = "") -> None:
        msg = (
            f"Invoice number '{invoice_number}' already exists."
            if invoice_number
            else "Duplicate invoice number."
        )
        super().__init__(msg)
