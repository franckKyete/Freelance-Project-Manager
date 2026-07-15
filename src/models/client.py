"""Client model — inherits from Person."""

from .person import Person


class Client(Person):
    """Represents a client who commissions projects from the freelancer.

    Inherits all contact attributes from Person and adds company and
    billing preference information.

    Attributes (private):
        __company_name: Name of the client's company or organisation.
        __address: Physical or billing address.
        __preferred_payment_method: How the client prefers to be invoiced.
    """

    PAYMENT_METHODS = ("Bank Transfer", "PayPal", "Cash", "Cheque", "Credit Card", "Crypto")

    def __init__(
        self,
        full_name: str,
        email: str,
        phone: str = "",
        company_name: str = "",
        address: str = "",
        preferred_payment_method: str = "Bank Transfer",
        client_id: int = 0,
    ) -> None:
        """Initialise a Client.

        Args:
            full_name: Client's contact name.
            email: Client's email address.
            phone: Client's phone number.
            company_name: Name of the client's company.
            address: Physical or billing address.
            preferred_payment_method: Payment preference string.
            client_id: Database primary key.
        """
        super().__init__(full_name, email, phone, client_id)
        self.__company_name: str = company_name.strip()
        self.__address: str = address.strip()
        self.preferred_payment_method = preferred_payment_method  # uses setter

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def company_name(self) -> str:
        """str: The client's company or organisation name."""
        return self.__company_name

    @company_name.setter
    def company_name(self, value: str) -> None:
        self.__company_name = value.strip()

    @property
    def address(self) -> str:
        """str: The client's billing or physical address."""
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        self.__address = value.strip()

    @property
    def preferred_payment_method(self) -> str:
        """str: The client's preferred payment method."""
        return self.__preferred_payment_method

    @preferred_payment_method.setter
    def preferred_payment_method(self, value: str) -> None:
        self.__preferred_payment_method = value.strip()

    # ------------------------------------------------------------------ #
    # Abstract method implementations
    # ------------------------------------------------------------------ #

    def display_information(self) -> str:
        """Return a formatted summary of the client's details.

        Returns:
            Multi-line string with all client contact details.
        """
        lines = [
            f"Name   : {self.full_name}",
            f"Company: {self.company_name or 'N/A'}",
            f"Email  : {self.email}",
            f"Phone  : {self.phone or 'N/A'}",
            f"Address: {self.address or 'N/A'}",
            f"Payment: {self.preferred_payment_method}",
        ]
        return "\n".join(lines)

    def validate_contact(self) -> bool:
        """Verify that the client has at minimum a name and email.

        Returns:
            True if full_name and email are both non-empty.
        """
        return bool(self.full_name and self.email)

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def get_projects(self, project_repository) -> list:
        """Retrieve all projects belonging to this client.

        Args:
            project_repository: A ProjectRepository instance.

        Returns:
            List of Project objects associated with this client.
        """
        return project_repository.find_by_client(self.id)

    def to_dict(self) -> dict:
        """Serialise the client to a plain dictionary for persistence.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "company_name": self.company_name,
            "address": self.address,
            "preferred_payment_method": self.preferred_payment_method,
        }
