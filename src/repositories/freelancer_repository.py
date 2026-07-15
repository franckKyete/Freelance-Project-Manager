"""FreelancerRepository — stores/retrieves the single freelancer profile."""

from typing import Optional
from src.models.person import Freelancer, SeniorFreelancer
from src.exceptions.app_exceptions import ProfileNotFoundException
from ._base import get_db


class FreelancerRepository:
    """Handles persistence of the freelancer profile (one row, id=1)."""

    PROFILE_ID = 1  # The system stores exactly one profile.

    def save(self, freelancer: Freelancer) -> Freelancer:
        """Insert or replace the freelancer profile record."""
        db = get_db()
        is_senior = isinstance(freelancer, SeniorFreelancer)
        yoe = getattr(freelancer, "years_of_experience", 0) if is_senior else 0

        try:
            db.execute(
                """
                INSERT OR REPLACE INTO freelancer_profile
                    (id, full_name, email, phone, profession, hourly_rate,
                     years_of_experience, is_senior)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.PROFILE_ID, freelancer.full_name, freelancer.email,
                    freelancer.phone, freelancer.profession, freelancer.hourly_rate,
                    yoe, int(is_senior),
                ),
            )
            db.commit()
            freelancer.id = self.PROFILE_ID
        except Exception as exc:
            raise RuntimeError(f"FreelancerRepository.save failed: {exc}") from exc
        return freelancer

    def load(self) -> Freelancer:
        """Load the freelancer profile from the database.

        Returns:
            A Freelancer (or SeniorFreelancer) instance.

        Raises:
            ProfileNotFoundException: If no profile row exists.
        """
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM freelancer_profile WHERE id=?", (self.PROFILE_ID,)
        )
        row = cursor.fetchone()
        if row is None:
            raise ProfileNotFoundException()

        if row["is_senior"]:
            return SeniorFreelancer(
                full_name=row["full_name"],
                email=row["email"],
                phone=row["phone"],
                profession=row["profession"],
                hourly_rate=row["hourly_rate"],
                years_of_experience=row["years_of_experience"],
                person_id=row["id"],
            )
        return Freelancer(
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            profession=row["profession"],
            hourly_rate=row["hourly_rate"],
            person_id=row["id"],
        )

    def exists(self) -> bool:
        """Return True if a profile record already exists."""
        db = get_db()
        cursor = db.execute(
            "SELECT 1 FROM freelancer_profile WHERE id=?", (self.PROFILE_ID,)
        )
        return cursor.fetchone() is not None
