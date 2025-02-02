from sqlalchemy import Boolean, Column, Integer, String, BigInteger, Text
from ..db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    kyc = Column(Boolean, default=False)
    wallet_address = Column(String, nullable=True)
    private_key = Column(String, nullable=True)  # Store private key for hackathon
    full_name = Column(String, nullable=True)
    birthday = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    class Config:
        orm_mode = True
