from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.user import User as UserModel
from ...schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.telegram_id == user.telegram_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    db_user = UserModel(
        telegram_id=user.telegram_id,
        username=user.username,
        wallet_address=user.wallet_address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{telegram_id}", response_model=User)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{telegram_id}", response_model=User)
def update_user(telegram_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[User])
def list_users(
    kyc: Optional[bool] = Query(None, description="Filter users by KYC status"),
    db: Session = Depends(get_db)
):
    query = db.query(UserModel)
    if kyc is not None:
        query = query.filter(UserModel.kyc == kyc)
    return query.all()
