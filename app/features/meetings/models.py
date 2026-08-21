from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class MeetGroup(Base, AuditMixin):
    __tablename__ = "meet_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))


class MeetGroupUser(Base, AuditMixin):
    __tablename__ = "meet_group_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    meet_group_id: Mapped[int] = mapped_column(ForeignKey("meet_groups.id"))


class Meet(Base, AuditMixin):
    __tablename__ = "meets"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"))
    meet_group_id: Mapped[int] = mapped_column(ForeignKey("meet_groups.id"))
