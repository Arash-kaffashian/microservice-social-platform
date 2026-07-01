from fastapi import HTTPException, status
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from .. import models, schemas


""" notification crud """


# get my notifications and its total number
def get_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    query = (
        db.query(models.Notification)
        .filter(
            or_(
                models.Notification.is_public.is_(True),
                and_(
                    models.Notification.is_public.is_(False),
                    models.Notification.recipient_id == user_id,
                ),
            )
        )
    )

    total = query.count()

    items = (
        query.order_by(models.Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total

# get admin private notifications and all public notifications
def get_all_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 20,):
    query = (
        db.query(models.Notification)
        .filter(
            models.Notification.type == "admin_message",
            or_(
                models.Notification.is_public.is_(True),
                and_(
                    models.Notification.is_public.is_(False),
                    models.Notification.actor_id == user_id,
                ),
            ),
        )
    )

    total = query.count()

    items = (
        query.order_by(models.Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total

# get one notification by owner
def get_notification(db: Session, user_id: int, notification_id: int):
    notification_db = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification_db:
        raise HTTPException(status_code=404, detail="notification not found!")
    if notification_db.is_public == False and notification_db.recipient_id != user_id:
        raise HTTPException(status_code=403, detail="only the notification recipient can view this notification!")

    return notification_db

# create public or private notification by admin
def create_notification(db: Session, notification: schemas.NotificationInput):
    if notification.is_public and notification.recipient_id is not None:
        raise ValueError("public notifications must not have recipient_id")

    if not notification.is_public and notification.recipient_id is None:
        raise ValueError("for private notifications recipient_id is required")

    payload_data = notification.payload.dict() if notification.payload else None

    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=notification.expire_days)
        if notification.expire_days else None
    )

    db_notification = models.Notification(
        recipient_id=notification.recipient_id,
        actor_id=notification.actor_id,
        type=notification.type,
        object_type=notification.object_type,
        object_id=notification.object_id,
        expires_at=expires_at,
        payload=payload_data,
        is_public=notification.is_public
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

# delete one notification by admin
def delete_notification(db: Session, notification_id:int):
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="notification not found!")

    if notification.type != "admin_message":
        raise HTTPException(status_code=403, detail="you cannot delete this notification")

    db.delete(notification)
    db.commit()

    return "notification successfully deleted!"

# delete all notifications of one user (user_deleted)
def delete_user_notifications(db: Session, user_id:int):
    notifications = db.query(models.Notification).filter(models.Notification.recipient_id == user_id).all()

    for notification in notifications:
        db.delete(notification)

    db.commit()

    return None

# delete notification of one object (object_deleted)
def delete_object_notification(db: Session, object_type:str, object_id:int):
    notification = db.query(models.Notification).filter(models.Notification.object_type == object_type, models.Notification.object_id == object_id).first()

    db.delete(notification)
    db.commit()

    return notification

# update nickname for all user notifications (user_updated)
def update_actor_nickname(db: Session, user_id:int, nickname:str):
    db.query(models.Notification).filter(
        models.Notification.type == "user_created",
        models.Notification.actor_id == user_id
    ).update(
        {models.Notification.payload: {"message": f"{nickname} joined us!"}},
        synchronize_session=False)

    db.query(models.Notification).filter(
        models.Notification.type == "post_created",
        models.Notification.actor_id == user_id
    ).update(
        {models.Notification.payload: {"message": f"{nickname} recently posted!"}},
        synchronize_session=False)

    db.query(models.Notification).filter(
        models.Notification.type == "comment_created",
        models.Notification.actor_id == user_id
    ).update(
        {models.Notification.payload: {"message": f"{nickname} replied on your comment!"}},
        synchronize_session=False)

    db.commit()

    return None

# update one notification by admin
def update_notification(db: Session, notification_id: int, actor_id: int, message: str):
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="notification not found!"
        )

    if notification.type != "admin_message":
        raise HTTPException(
            status_code=403,
            detail="you cannot update this notification"
        )

    notification.payload = {"message": message}
    notification.actor_id = actor_id

    db.commit()
    db.refresh(notification)

    return notification