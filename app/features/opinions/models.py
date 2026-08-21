import enum

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class Sentiment(enum.IntEnum):
    STRONGLY_DISLIKE = 1
    DISLIKE = 2
    INDIFFERENT = 3
    LIKE = 4
    STRONGLY_LIKE = 5


class UserOpinion(Base, AuditMixin):
    __tablename__ = "user_opinions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(1000))
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    sentiment: Mapped[int] = mapped_column(SmallInteger)
