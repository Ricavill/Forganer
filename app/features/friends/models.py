import enum

from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class InvitationStatus(enum.IntEnum):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3


class UserFriends(Base, AuditMixin):
    __tablename__ = "user_friends"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class UserFriendsMember(Base, AuditMixin):
    __tablename__ = "user_friends_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_friends_id: Mapped[int] = mapped_column(ForeignKey("user_friends.id"))


class FriendInvitation(Base, AuditMixin):
    __tablename__ = "friend_invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[int] = mapped_column(SmallInteger, default=InvitationStatus.PENDING)
