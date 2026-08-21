import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class Sentiment(str, enum.Enum):
    STRONGLY_LIKE = "strongly_like"
    LIKE = "like"
    INDIFFERENT = "indifferent"
    DISLIKE = "dislike"
    STRONGLY_DISLIKE = "strongly_dislike"


class UserOpinion(Base, AuditMixin):
    __tablename__ = "user_opinions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(1000))
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    sentiment: Mapped[Sentiment] = mapped_column(Enum(Sentiment, name="sentiment"))
