from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.features.friends.models import FriendInvitation, InvitationStatus, UserFriends, UserFriendsMember
from app.features.friends.schemas import FriendInvitationOut, FriendOut, InterestedFriendOut
from app.features.opinions.service import list_positive_opinions_for_users
from app.features.users.models import User
from app.features.users.service import get_users_by_ids


def _invitations_to_out(db: Session, invitations: list[FriendInvitation]) -> list[FriendInvitationOut]:
    if not invitations:
        return []
    user_ids = {inv.from_user_id for inv in invitations} | {inv.to_user_id for inv in invitations}
    users_by_id = {u.id: u for u in get_users_by_ids(db, list(user_ids))}
    return [
        FriendInvitationOut(
            id=inv.id,
            from_user=FriendOut.model_validate(users_by_id[inv.from_user_id]),
            to_user=FriendOut.model_validate(users_by_id[inv.to_user_id]),
            status=inv.status,
            created_at=inv.created_at,
        )
        for inv in invitations
    ]


def _invitation_to_out(db: Session, invitation: FriendInvitation) -> FriendInvitationOut:
    return _invitations_to_out(db, [invitation])[0]


def _get_or_create_circle(db: Session, user_id: int) -> UserFriends:
    circle = db.execute(select(UserFriends).where(UserFriends.user_id == user_id)).scalar_one_or_none()
    if circle is None:
        circle = UserFriends(user_id=user_id)
        db.add(circle)
        db.flush()
    return circle


def get_friend_user_ids(db: Session, user_id: int) -> list[int]:
    circle = db.execute(select(UserFriends).where(UserFriends.user_id == user_id)).scalar_one_or_none()
    if circle is None:
        return []
    result = db.execute(
        select(UserFriendsMember.user_id).where(UserFriendsMember.user_friends_id == circle.id)
    )
    return [row[0] for row in result.all()]


def _are_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    return user_b_id in get_friend_user_ids(db, user_a_id)


def _has_pending_invitation(db: Session, user_a_id: int, user_b_id: int) -> bool:
    result = db.execute(
        select(FriendInvitation).where(
            FriendInvitation.status == InvitationStatus.PENDING,
            FriendInvitation.deleted_at.is_(None),
            ((FriendInvitation.from_user_id == user_a_id) & (FriendInvitation.to_user_id == user_b_id))
            | ((FriendInvitation.from_user_id == user_b_id) & (FriendInvitation.to_user_id == user_a_id)),
        )
    )
    return result.first() is not None


def send_request(db: Session, from_user_id: int, to_user_id: int) -> FriendInvitationOut:
    if from_user_id == to_user_id:
        raise ValidationError("You cannot send a friend request to yourself")

    if _are_friends(db, from_user_id, to_user_id):
        raise ConflictError("You are already friends with this user")

    if _has_pending_invitation(db, from_user_id, to_user_id):
        raise ConflictError("A pending friend request already exists between these users")

    invitation = FriendInvitation(from_user_id=from_user_id, to_user_id=to_user_id)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return _invitation_to_out(db, invitation)


def list_incoming_requests(db: Session, user_id: int) -> list[FriendInvitationOut]:
    result = db.execute(
        select(FriendInvitation).where(
            FriendInvitation.to_user_id == user_id,
            FriendInvitation.status == InvitationStatus.PENDING,
            FriendInvitation.deleted_at.is_(None),
        )
    )
    return _invitations_to_out(db, list(result.scalars().all()))


def list_sent_requests(db: Session, user_id: int) -> list[FriendInvitationOut]:
    result = db.execute(
        select(FriendInvitation).where(
            FriendInvitation.from_user_id == user_id,
            FriendInvitation.status == InvitationStatus.PENDING,
            FriendInvitation.deleted_at.is_(None),
        )
    )
    return _invitations_to_out(db, list(result.scalars().all()))


def _get_pending_invitation_for_recipient(db: Session, invitation_id: int, user_id: int) -> FriendInvitation:
    result = db.execute(
        select(FriendInvitation).where(
            FriendInvitation.id == invitation_id,
            FriendInvitation.to_user_id == user_id,
            FriendInvitation.deleted_at.is_(None),
        )
    )
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise NotFoundError("Friend request not found")
    if invitation.status != InvitationStatus.PENDING:
        raise ConflictError("This friend request has already been responded to")
    return invitation


def cancel_request(db: Session, invitation_id: int, user_id: int) -> None:
    """Withdraw a friend request you sent, as long as it's still pending."""
    result = db.execute(
        select(FriendInvitation).where(
            FriendInvitation.id == invitation_id,
            FriendInvitation.from_user_id == user_id,
            FriendInvitation.deleted_at.is_(None),
        )
    )
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise NotFoundError("Friend request not found")
    if invitation.status != InvitationStatus.PENDING:
        raise ConflictError("This friend request has already been responded to")

    invitation.deleted_at = datetime.now(timezone.utc)
    db.commit()


def accept_request(db: Session, invitation_id: int, user_id: int) -> FriendInvitationOut:
    invitation = _get_pending_invitation_for_recipient(db, invitation_id, user_id)

    invitation.status = InvitationStatus.ACCEPTED

    circle_a = _get_or_create_circle(db, invitation.from_user_id)
    circle_b = _get_or_create_circle(db, invitation.to_user_id)
    db.add(UserFriendsMember(user_id=invitation.to_user_id, user_friends_id=circle_a.id))
    db.add(UserFriendsMember(user_id=invitation.from_user_id, user_friends_id=circle_b.id))

    db.commit()
    db.refresh(invitation)
    return _invitation_to_out(db, invitation)


def reject_request(db: Session, invitation_id: int, user_id: int) -> FriendInvitationOut:
    invitation = _get_pending_invitation_for_recipient(db, invitation_id, user_id)
    invitation.status = InvitationStatus.REJECTED
    db.commit()
    db.refresh(invitation)
    return _invitation_to_out(db, invitation)


def list_friends(db: Session, user_id: int) -> list[User]:
    friend_ids = get_friend_user_ids(db, user_id)
    return get_users_by_ids(db, friend_ids)


def list_interested_friends(db: Session, user_id: int, activity_id: int) -> list[InterestedFriendOut]:
    """Friends of `user_id` with a positive (LIKE or STRONGLY_LIKE) opinion about `activity_id`."""
    friend_ids = get_friend_user_ids(db, user_id)
    opinions = list_positive_opinions_for_users(db, friend_ids, activity_id)
    if not opinions:
        return []

    friends_by_id = {u.id: u for u in get_users_by_ids(db, [o.user_id for o in opinions])}
    return [
        InterestedFriendOut(
            user_id=opinion.user_id,
            name=friends_by_id[opinion.user_id].name,
            last_name=friends_by_id[opinion.user_id].last_name,
            sentiment=opinion.sentiment,
        )
        for opinion in opinions
    ]
