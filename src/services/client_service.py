"""ClientService — business logic for client management."""

from typing import List, Optional
from src.models.client import Client
from src.repositories.client_repository import ClientRepository
from src.exceptions.app_exceptions import (
    ClientNotFoundException, DuplicateClientEmailException, DuplicateClientPhoneException,
)
from src.utils.validators import validate_email, sanitize_string


class ClientService:
    """Provides business-level operations for managing clients.

    Wraps ClientRepository and enforces validation rules.

    Example:
        service = ClientService()
        client = service.create("Alice", "alice@example.com")
    """

    def __init__(self) -> None:
        self._repo = ClientRepository()

    def create(
        self,
        full_name: str,
        email: str,
        phone: str = "",
        company_name: str = "",
        address: str = "",
        preferred_payment_method: str = "Bank Transfer",
    ) -> Client:
        """Create and persist a new client.

        Args:
            full_name: Client's contact name.
            email: Client's email address.
            phone: Phone number.
            company_name: Company name.
            address: Physical address.
            preferred_payment_method: Payment preference.

        Returns:
            The saved Client with its assigned id.

        Raises:
            ValueError: If name is empty or email is invalid.
            DuplicateClientEmailException: If email already exists.
            DuplicateClientPhoneException: If phone number already exists.
        """
        # Uniqueness checks
        existing_email = self._repo.find_by_email(email)
        if existing_email:
            raise DuplicateClientEmailException(email)
        if phone:
            existing_phone = self._repo.find_by_phone(phone)
            if existing_phone:
                raise DuplicateClientPhoneException(phone)

        try:
            client = Client(
                full_name=sanitize_string(full_name),
                email=email,
                phone=sanitize_string(phone),
                company_name=sanitize_string(company_name),
                address=sanitize_string(address),
                preferred_payment_method=preferred_payment_method,
            )
        except ValueError as exc:
            raise ValueError(f"Invalid client data: {exc}") from exc
        return self._repo.save(client)


    def update(self, client: Client) -> Client:
        """Update an existing client's details.

        Args:
            client: The Client instance with updated fields.

        Returns:
            The updated Client.

        Raises:
            ClientNotFoundException: If the client does not exist in the DB.
            DuplicateClientEmailException: If email already belongs to another client.
            DuplicateClientPhoneException: If phone number already belongs to another client.
        """
        existing = self._repo.find_by_id(client.id)
        if existing is None:
            raise ClientNotFoundException(client.id)

        # Uniqueness checks (excluding current client id)
        existing_email = self._repo.find_by_email(client.email)
        if existing_email and existing_email.id != client.id:
            raise DuplicateClientEmailException(client.email)
        if client.phone:
            existing_phone = self._repo.find_by_phone(client.phone)
            if existing_phone and existing_phone.id != client.id:
                raise DuplicateClientPhoneException(client.phone)

        return self._repo.save(client)


    def delete(self, client_id: int) -> None:
        """Delete a client by id.

        Args:
            client_id: The id of the client to delete.

        Raises:
            ClientNotFoundException: If the client does not exist.
        """
        if not self._repo.find_by_id(client_id):
            raise ClientNotFoundException(client_id)
        try:
            self._repo.delete(client_id)
        except Exception as exc:
            raise RuntimeError(f"Failed to delete client {client_id}: {exc}") from exc
        else:
            pass  # delete succeeded
        finally:
            pass  # cleanup would go here if needed

    def get_all(self) -> List[Client]:
        """Retrieve all clients.

        Returns:
            List of all Client instances.
        """
        return self._repo.find_all()

    def get_by_id(self, client_id: int) -> Client:
        """Retrieve a client by id.

        Args:
            client_id: The client's database id.

        Returns:
            The matching Client.

        Raises:
            ClientNotFoundException: If not found.
        """
        client = self._repo.find_by_id(client_id)
        if client is None:
            raise ClientNotFoundException(client_id)
        return client

    def search(self, query: str) -> List[Client]:
        """Search clients by name or company.

        Args:
            query: Partial name or company string.

        Returns:
            List of matching clients.
        """
        return self._repo.search(query)
