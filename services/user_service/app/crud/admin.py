from sqlalchemy.orm import Session
from decouple import config

from ..core.security import hash_password
from ..models import User


""" admins crud """


# auto create or promote superadmin on start
def create_superadmin(db: Session):
    superadmin_email = config("SUPERADMIN_EMAIL")

    user = db.query(User).filter(User.email == superadmin_email).first()

    if not user:
        user = User(
            email=config("SUPERADMIN_EMAIL"),
            username="superadmin",
            nickname="superadmin",
            hashed_password= hash_password(config("SUPERADMIN_PASSWORD")),
            role="superadmin",
            is_email_verified=True
        )
        db.add(user)
        db.commit()
        print("SuperAdmin created")
    else:
        if user.role != "superadmin":
            user.role = "superadmin"
            user.nickname = "superadmin"
            user.hashed_password = hash_password(config("SUPERADMIN_PASSWORD"))
            user.is_email_verified = True
            db.commit()
            print("SuperAdmin role restored")
