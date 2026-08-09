from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    room_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    price_per_night: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="available",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    hotel = relationship(
        "Hotel",
        back_populates="rooms",
    )
