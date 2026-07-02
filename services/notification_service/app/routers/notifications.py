from fastapi import FastAPI, Depends, HTTPException, APIRouter, status, Query
from sqlalchemy.orm import Session

from .. import schemas, database, dependencies
from ..crud import notifications


""" comments routers """


router = APIRouter()

# get one user all notifications paginated list
@router.get("/notifications/", dependencies=[Depends(dependencies.get_current_user)], response_model=schemas.PaginatedNotificationResponse)
def read_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db),
    user=Depends(dependencies.get_current_user),
):
    items, total = notifications.get_notifications(
        db=db,
        user_id=user["user_id"],
        skip=skip,
        limit=limit,
    )

    return {
        "items": items,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    }

# get admin all private and public notifications paginated list
@router.get("/admin/notifications/", dependencies=[Depends(dependencies.admin_required)], response_model=schemas.PaginatedNotificationResponse)
def read_admin_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db),
    user=Depends(dependencies.get_current_user),
):
    items, total = notifications.get_admin_notifications(
        db=db,
        user_id=user["user_id"],
        skip=skip,
        limit=limit,
    )

    return {
        "items": items,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    }

# get one notification by owner
@router.get("/notifications/{notification_id}", dependencies=[Depends(dependencies.get_current_user)], response_model=schemas.NotificationSchema)
def read_notification(
    notification_id:int,
    db: Session = Depends(database.get_db),
    user=Depends(dependencies.get_current_user),
):
    user_id = user["user_id"]

    return notifications.get_notification(db,user_id,notification_id)

# create notification by admin
@router.post("/admin/notifications/", dependencies=[Depends(dependencies.admin_required)], response_model=schemas.NotificationSchema)
def create_notification_by_admin(
    notif: schemas.CreateNotificationInput,
    db: Session = Depends(database.get_db),
    user=Depends(dependencies.get_current_user)
):
    admin_id = user["user_id"]

    notification = schemas.NotificationInput(
        recipient_id=notif.recipient_id,
        actor_id=admin_id,
        type="admin_message",
        object_type=None,
        object_id=None,
        expire_days=3,
        payload=schemas.NotificationPayloadData(message=notif.message),
        is_public=notif.is_public,
    )

    try:
        return notifications.create_notification(db, notification)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# update notification by admin
@router.patch("/admin/notifications/{notification_id}/", dependencies=[Depends(dependencies.admin_required)], response_model=schemas.NotificationSchema)
def update_notification_by_admin(
    notification_id: int,
    input: schemas.UpdateNotificationInput,
    db: Session = Depends(database.get_db),
    user=Depends(dependencies.get_current_user)
):
    admin_id = user["user_id"]

    return notifications.update_notification(db, notification_id, admin_id, input.message)

# delete notification by admin
@router.delete("/admin/notifications/{notification_id}/", dependencies=[Depends(dependencies.admin_required)], status_code=status.HTTP_200_OK)
def delete_notification_by_admin(
    notification_id: int,
    db: Session = Depends(database.get_db)
):
    return notifications.delete_notification(db, notification_id)