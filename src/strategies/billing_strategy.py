"""Billing Strategy hierarchy — Strategy design pattern.

Design Pattern: **Strategy**
BillingStrategy (ABC) defines a common interface.
Concrete strategies implement different billing calculations.
Project delegates invoice amount calculation to its strategy.

Example:
    project.billing_strategy = HourlyBilling()
    amount = project.calculate_invoice_amount()
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.project import Project


class BillingStrategy(ABC):
    """Abstract base class for all billing strategies.

    Concrete subclasses must implement calculate_invoice() to provide
    the actual billing logic.
    """

    @abstractmethod
    def calculate_invoice(self, project: "Project") -> float:
        """Calculate the billable amount for the given project.

        Args:
            project: The Project instance whose data drives the calculation.

        Returns:
            The calculated invoice total as a float.
        """

    @abstractmethod
    def description(self) -> str:
        """Return a short human-readable description of this billing strategy.

        Returns:
            Strategy description string.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class HourlyBilling(BillingStrategy):
    """Bill the client based on hours actually logged multiplied by a rate.

    Formula: total_hours_logged × billing_rate
    """

    def calculate_invoice(self, project: "Project") -> float:
        """Calculate the invoice as hours × rate.

        Args:
            project: Project instance providing total_hours_logged()
                     and billing_rate.

        Returns:
            total_hours_logged × billing_rate.
        """
        return project.total_hours_logged() * project.billing_rate

    def description(self) -> str:
        """Return a description of the hourly billing model.

        Returns:
            Human-readable description string.
        """
        return "Hourly Billing: hours logged × hourly rate"


class FixedPriceBilling(BillingStrategy):
    """Bill the client a fixed price regardless of hours worked.

    Formula: billing_rate (treated as the agreed fixed price)
    """

    def calculate_invoice(self, project: "Project") -> float:
        """Return the project's fixed billing_rate as the invoice amount.

        Args:
            project: Project instance providing billing_rate.

        Returns:
            project.billing_rate as a fixed price.
        """
        return project.billing_rate

    def description(self) -> str:
        """Return a description of the fixed-price billing model.

        Returns:
            Human-readable description string.
        """
        return "Fixed Price Billing: agreed lump-sum price"


class RetainerBilling(BillingStrategy):
    """Bill the client a recurring monthly retainer fee.

    Formula: billing_rate × months_active (derived from start/deadline dates)
    Falls back to billing_rate × 1 if dates are unavailable.
    """

    def calculate_invoice(self, project: "Project") -> float:
        """Calculate the retainer invoice based on project duration.

        Derives the number of whole months from start_date to deadline.
        Falls back to 1 month if dates are unparseable.

        Args:
            project: Project instance providing billing_rate, start_date,
                     and deadline.

        Returns:
            billing_rate × number_of_months.
        """
        months = self._months_between(project.start_date, project.deadline)
        return project.billing_rate * max(months, 1)

    def description(self) -> str:
        """Return a description of the retainer billing model.

        Returns:
            Human-readable description string.
        """
        return "Retainer Billing: monthly fee × project duration"

    @staticmethod
    def _months_between(start: str, end: str) -> int:
        """Compute the number of whole months between two ISO 8601 date strings.

        Args:
            start: ISO 8601 start date (e.g. '2025-01-15').
            end: ISO 8601 end date.

        Returns:
            Number of whole months, minimum 1.
        """
        try:
            from datetime import date
            s = date.fromisoformat(start)
            e = date.fromisoformat(end)
            return max((e.year - s.year) * 12 + (e.month - s.month), 1)
        except (ValueError, TypeError):
            return 1


# Convenience mapping used by the factory and GUI
STRATEGY_MAP: dict = {
    "hourly": HourlyBilling,
    "fixed": FixedPriceBilling,
    "retainer": RetainerBilling,
}


def get_strategy(billing_type: str) -> BillingStrategy:
    """Instantiate and return the correct BillingStrategy for a billing type.

    Args:
        billing_type: One of 'hourly', 'fixed', 'retainer'.

    Returns:
        An instance of the corresponding BillingStrategy subclass.

    Raises:
        InvalidBillingStrategyException: If billing_type is not recognised.
    """
    from src.exceptions.app_exceptions import InvalidBillingStrategyException
    cls = STRATEGY_MAP.get(billing_type.lower())
    if cls is None:
        raise InvalidBillingStrategyException(billing_type)
    return cls()
