from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.user import User as UserModel
from ...schemas.user import User, UserCreate, UserUpdate
from ...services.wallet_wrapper import WalletService
from ...bot.bot import notify_kyc_approved

logger = logging.getLogger(__name__)

router = APIRouter()
wallet_service = WalletService()


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
async def update_user(telegram_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        # Handle KYC approval
        if update_data.get('kyc'):
            # Create wallet if needed
            if not db_user.wallet_address:
                try:
                    wallet = await wallet_service.create_wallet()
                    print(f"Wallet created: {wallet}")  # Debug log
                    db_user.wallet_address = wallet['address']
                    db_user.private_key = wallet['privateKey']
                except Exception as e:
                    print(f"Error creating wallet: {str(e)}")  # Debug log
                    raise HTTPException(status_code=500, detail=f"Error creating wallet: {str(e)}")
            
            # Commit changes first
            db.commit()
            db.refresh(db_user)
            
            # Send notification after commit (so even if notification fails, DB is updated)
            try:
                await notify_kyc_approved(db_user.telegram_id, db_user.wallet_address)
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                # Don't raise error, just log it since the KYC approval itself succeeded
            
            return db_user
    except Exception as e:
        print(f"Error updating user: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.get("/", response_model=List[User])
def list_users(
    kyc: Optional[bool] = Query(None, description="Filter users by KYC status"),
    db: Session = Depends(get_db)
):
    query = db.query(UserModel)
    if kyc is not None:
        query = query.filter(UserModel.kyc == kyc)
    return query.all()
