from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dependencies import superadmin_required
from .. import database
from ..core import rate_limit
from ..models import User


""" admin panel routers """


# # routers prefix configuration
router = APIRouter(prefix="/settings", tags=["settings"])

# create admin API for superadmin to promote normal users to admin by their id
@router.post("/admins",dependencies=[Depends(superadmin_required), rate_limit.rate_limit(limit=5, window=300)])
def create_admin(user_id: int,db: Session = Depends(database.get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.role=="superadmin":
        raise HTTPException(400, "this user has already been assigned superadmin.")
    if user.role=="admin":
        raise HTTPException(400, "this user has already been assigned admin.")
    user.role = "admin"
    db.commit()

    return {"message": "Admin created"}
