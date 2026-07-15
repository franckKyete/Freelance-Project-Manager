"""Person abstract base class, Freelancer, and SeniorFreelancer models.

Inheritance chain (3 levels):
    Person (ABC) → Freelancer → SeniorFreelancer
"""

import re
from abc import ABC, abstractmethod
from typing import Optional


class Person(ABC):
    """Abstract base class representing any person in the system.

    Attributes (private):
        __id: Unique identifier.
        __full_name: Full display name.
        __email: Contact email address.
        __phone: Contact phone number.
    """

    def __init__(
        self,
        full_name: str,
        email: str,
        phone: str = "",
        person_id: int = 0,
    ) -> None:
        """Initialise a Person.

        Args:
            full_name: The person's full name (non-empty string).
            email: Valid email address.
            phone: Optional phone number string.
            person_id: Database primary-key id (0 means not yet persisted).

        Raises:
            ValueError: If full_name is empty or email format is invalid.
        """
        self.__id: int = person_id
        self.full_name = full_name  # uses setter
        self.email = email          # uses setter
        self.__phone: str = phone

    # ------------------------------------------------------------------ #
    # Properties — id
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> int:
        """int: Database primary key (read-only after first assignment)."""
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        if value < 0:
            raise ValueError("id must be a non-negative integer.")
        self.__id = value

    # ------------------------------------------------------------------ #
    # Properties — full_name
    # ------------------------------------------------------------------ #

    @property
    def full_name(self) -> str:
        """str: The person's full name."""
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("full_name cannot be empty.")
        self.__full_name = value

    # ------------------------------------------------------------------ #
    # Properties — email
    # ------------------------------------------------------------------ #

    @property
    def email(self) -> str:
        """str: The person's email address."""
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        value = value.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError(f"'{value}' is not a valid email address.")
        self.__email = value

    # ------------------------------------------------------------------ #
    # Properties — phone
    # ------------------------------------------------------------------ #

    @property
    def phone(self) -> str:
        """str: The person's phone number."""
        return self.__phone

    @phone.setter
    def phone(self, value: str) -> None:
        self.__phone = value.strip()

    # ------------------------------------------------------------------ #
    # Abstract methods (must be implemented by concrete subclasses)
    # ------------------------------------------------------------------ #

    @abstractmethod
    def display_information(self) -> str:
        """Return a formatted string with the person's details.

        Returns:
            Multi-line string representation of the person.
        """

    @abstractmethod
    def validate_contact(self) -> bool:
        """Check that the minimum contact details are present and valid.

        Returns:
            True if all required contact fields are filled.
        """

    # ------------------------------------------------------------------ #
    # Dunder helpers
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__id}, name='{self.__full_name}')"


# ====================================================================== #
# Freelancer  (Person → Freelancer)                                       #
# ====================================================================== #

class Freelancer(Person):
    """Represents the freelancer who owns and operates the application.

    Inherits from Person and adds profession, hourly_rate, and tax_number.

    Attributes (private):
        __profession: The freelancer's field of work.
        __hourly_rate: Standard billing rate per hour (>= 0).
        __tax_number: Official tax identification number.
    """

    def __init__(
        self,
        full_name: str,
        email: str,
        phone: str = "",
        profession: str = "",
        hourly_rate: float = 0.0,
        tax_number: str = "",
        person_id: int = 0,
    ) -> None:
        """Initialise a Freelancer.

        Args:
            full_name: Full name (delegated to Person).
            email: Email address (delegated to Person).
            phone: Phone number (delegated to Person).
            profession: Professional title / field.
            hourly_rate: Default billing rate per hour (must be >= 0).
            tax_number: Tax/VAT identification number.
            person_id: Database primary key.

        Raises:
            ValueError: If hourly_rate is negative.
        """
        super().__init__(full_name, email, phone, person_id)
        self.__profession: str = profession
        self.hourly_rate = hourly_rate  # uses setter for validation
        self.__tax_number: str = tax_number

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def profession(self) -> str:
        """str: The freelancer's profession."""
        return self.__profession

    @profession.setter
    def profession(self, value: str) -> None:
        self.__profession = value.strip()

    @property
    def hourly_rate(self) -> float:
        """float: The hourly billing rate (must be >= 0)."""
        return self.__hourly_rate

    @hourly_rate.setter
    def hourly_rate(self, value: float) -> None:
        if value < 0:
            raise ValueError("hourly_rate cannot be negative.")
        self.__hourly_rate = float(value)

    @property
    def tax_number(self) -> str:
        """str: The freelancer's tax identification number."""
        return self.__tax_number

    @tax_number.setter
    def tax_number(self, value: str) -> None:
        self.__tax_number = value.strip()

    # ------------------------------------------------------------------ #
    # Concrete implementations of abstract methods
    # ------------------------------------------------------------------ #

    def display_information(self) -> str:
        """Return a formatted summary of the freelancer's profile.

        Returns:
            Multi-line string with all freelancer details.
        """
        lines = [
            f"Name      : {self.full_name}",
            f"Email     : {self.email}",
            f"Phone     : {self.phone or 'N/A'}",
            f"Profession: {self.profession or 'N/A'}",
            f"Rate      : ${self.hourly_rate:.2f}/hr",
            f"Tax No.   : {self.tax_number or 'N/A'}",
        ]
        return "\n".join(lines)

    def validate_contact(self) -> bool:
        """Check that the freelancer has at minimum a name and email.

        Returns:
            True if both full_name and email are non-empty.
        """
        return bool(self.full_name and self.email)

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def create_project(self, title: str, client_id: int, budget: float) -> dict:
        """Build a project data dictionary ready for persistence.

        Args:
            title: Project title.
            client_id: The owning client's database id.
            budget: Agreed project budget.

        Returns:
            Dictionary with project field values.
        """
        return {
            "title": title,
            "client_id": client_id,
            "budget": budget,
            "billing_rate": self.hourly_rate,
        }

    def generate_report(self, report_type: str) -> str:
        """Return a placeholder report header.

        Args:
            report_type: One of 'income', 'expense', 'productivity', 'profit'.

        Returns:
            A formatted report title string.
        """
        return f"[{report_type.upper()} REPORT] — Prepared by {self.full_name}"


# ====================================================================== #
# SeniorFreelancer  (Person → Freelancer → SeniorFreelancer)              #
# ====================================================================== #

class SeniorFreelancer(Freelancer):
    """A senior freelancer with additional experience attributes.

    Inherits from Freelancer and extends it with years_of_experience
    and a premium_rate multiplier, satisfying the 3-level inheritance
    requirement.

    Attributes (private):
        __years_of_experience: Number of professional years (>= 0).
        __premium_rate: Rate multiplier applied on top of hourly_rate (>= 1.0).
    """

    def __init__(
        self,
        full_name: str,
        email: str,
        phone: str = "",
        profession: str = "",
        hourly_rate: float = 0.0,
        tax_number: str = "",
        years_of_experience: int = 0,
        premium_rate: float = 1.0,
        person_id: int = 0,
    ) -> None:
        """Initialise a SeniorFreelancer.

        Args:
            full_name: Full name.
            email: Email address.
            phone: Phone number.
            profession: Professional title.
            hourly_rate: Base billing rate per hour.
            tax_number: Tax identification number.
            years_of_experience: Years in the profession (must be >= 0).
            premium_rate: Multiplier applied to hourly_rate (must be >= 1.0).
            person_id: Database primary key.

        Raises:
            ValueError: If years_of_experience < 0 or premium_rate < 1.0.
        """
        super().__init__(
            full_name, email, phone, profession, hourly_rate, tax_number, person_id
        )
        self.years_of_experience = years_of_experience  # uses setter
        self.premium_rate = premium_rate                 # uses setter

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def years_of_experience(self) -> int:
        """int: Years of professional experience."""
        return self.__years_of_experience

    @years_of_experience.setter
    def years_of_experience(self, value: int) -> None:
        if value < 0:
            raise ValueError("years_of_experience must be >= 0.")
        self.__years_of_experience = int(value)

    @property
    def premium_rate(self) -> float:
        """float: Billing rate multiplier (>= 1.0)."""
        return self.__premium_rate

    @premium_rate.setter
    def premium_rate(self, value: float) -> None:
        if value < 1.0:
            raise ValueError("premium_rate must be >= 1.0.")
        self.__premium_rate = float(value)

    # ------------------------------------------------------------------ #
    # Overridden methods (method overriding)
    # ------------------------------------------------------------------ #

    def display_information(self) -> str:
        """Return an extended summary including senior-specific attributes.

        Overrides Freelancer.display_information().

        Returns:
            Multi-line string with all senior freelancer details.
        """
        base = super().display_information()
        extra = (
            f"Experience: {self.__years_of_experience} years\n"
            f"Premium × : {self.__premium_rate:.2f}"
        )
        return f"{base}\n{extra}"

    @property
    def effective_rate(self) -> float:
        """float: Actual billing rate after applying the premium multiplier."""
        return self.hourly_rate * self.__premium_rate
