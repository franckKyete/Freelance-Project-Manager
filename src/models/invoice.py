"""Invoice model — tracks client billing and payment status."""

from src.exceptions.app_exceptions import InvoiceAlreadyPaidException

INVOICE_STATUS = ("pending", "sent", "paid", "overdue", "cancelled")


class Invoice:
    """Represents a billing invoice issued to a client for a project.

    Attributes (private):
        __invoice_id: Database primary key.
        __invoice_number: Unique human-readable identifier (e.g. 'INV-2025-001').
        __client_id: FK of the client being billed.
        __project_id: FK of the related project.
        __amount: Invoice total in currency units (>= 0).
        __issue_date: ISO 8601 date the invoice was created.
        __due_date: ISO 8601 payment due date.
        __status: One of INVOICE_STATUS.
    """

    def __init__(
        self,
        invoice_number: str,
        client_id: int,
        project_id: int,
        amount: float = 0.0,
        issue_date: str = "",
        due_date: str = "",
        status: str = "pending",
        invoice_id: int = 0,
    ) -> None:
        """Initialise an Invoice.

        Args:
            invoice_number: Unique human-readable number (non-empty).
            client_id: FK of the client being billed.
            project_id: FK of the related project.
            amount: Invoice total (must be >= 0).
            issue_date: ISO 8601 issue date string.
            due_date: ISO 8601 due date string.
            status: One of INVOICE_STATUS.
            invoice_id: Database primary key.

        Raises:
            ValueError: If invoice_number is empty, amount negative,
                        or status invalid.
        """
        self.__invoice_id: int = invoice_id
        self.invoice_number = invoice_number    # setter validates
        self.__client_id: int = client_id
        self.__project_id: int = project_id
        self.amount = amount                    # setter validates
        self.__issue_date: str = issue_date
        self.__due_date: str = due_date
        self.status = status                    # setter validates

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def invoice_id(self) -> int:
        """int: Database primary key."""
        return self.__invoice_id

    @invoice_id.setter
    def invoice_id(self, value: int) -> None:
        self.__invoice_id = int(value)

    @property
    def invoice_number(self) -> str:
        """str: Unique human-readable invoice identifier."""
        return self.__invoice_number

    @invoice_number.setter
    def invoice_number(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("invoice_number cannot be empty.")
        self.__invoice_number = value

    @property
    def client_id(self) -> int:
        """int: FK of the client being billed."""
        return self.__client_id

    @client_id.setter
    def client_id(self, value: int) -> None:
        self.__client_id = int(value)

    @property
    def project_id(self) -> int:
        """int: FK of the related project."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value: int) -> None:
        self.__project_id = int(value)

    @property
    def amount(self) -> float:
        """float: Invoice total amount."""
        return self.__amount

    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise ValueError("Invoice amount cannot be negative.")
        self.__amount = float(value)

    @property
    def issue_date(self) -> str:
        """str: ISO 8601 issue date."""
        return self.__issue_date

    @issue_date.setter
    def issue_date(self, value: str) -> None:
        self.__issue_date = value.strip()

    @property
    def due_date(self) -> str:
        """str: ISO 8601 payment due date."""
        return self.__due_date

    @due_date.setter
    def due_date(self, value: str) -> None:
        self.__due_date = value.strip()

    @property
    def status(self) -> str:
        """str: Current invoice status."""
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        value = value.lower().strip()
        if value not in INVOICE_STATUS:
            raise ValueError(f"status must be one of {INVOICE_STATUS}.")
        self.__status = value

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def calculate_total(self) -> float:
        """Return the invoice total amount.

        Returns:
            The invoice amount as a float.
        """
        return self.__amount

    def mark_as_paid(self) -> None:
        """Set the invoice status to 'paid'.

        Raises:
            InvoiceAlreadyPaidException: If the invoice is already paid.
        """
        if self.__status == "paid":
            raise InvoiceAlreadyPaidException(self.__invoice_number)
        self.__status = "paid"

    def is_overdue(self, today: str) -> bool:
        """Check whether the invoice is overdue.

        Args:
            today: Today's date as an ISO 8601 string.

        Returns:
            True if due_date is set, status is not 'paid', and today > due_date.
        """
        if not self.__due_date or self.__status == "paid":
            return False
        return today > self.__due_date

    def to_dict(self) -> dict:
        """Serialise the invoice to a dictionary for persistence.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.__invoice_id,
            "invoice_number": self.__invoice_number,
            "client_id": self.__client_id,
            "project_id": self.__project_id,
            "amount": self.__amount,
            "issue_date": self.__issue_date,
            "due_date": self.__due_date,
            "status": self.__status,
        }

    def __repr__(self) -> str:
        return (
            f"Invoice(number='{self.__invoice_number}', "
            f"amount={self.__amount:.2f}, status='{self.__status}')"
        )
