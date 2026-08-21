from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class UserFriends(Base, AuditMixin):
    __tablename__ = "user_friends"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class UserFriendsMember(Base, AuditMixin):
    __tablename__ = "user_friends_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_friends_id: Mapped[int] = mapped_column(ForeignKey("user_friends.id"))
