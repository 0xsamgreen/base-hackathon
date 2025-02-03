"""Quiz models."""
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from ..db.session import Base

class Quiz(Base):
    """Quiz model."""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    reward_amount = Column(String, nullable=False)  # USDC reward amount as string
    eth_reward_amount = Column(String, nullable=False, default="0.00001")  # ETH reward

class UserQuizCompletion(Base):
    """User quiz completion model."""
    __tablename__ = "user_quiz_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    score = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    nft_token_id = Column(String)  # NFT token ID when minted
    nft_transaction_hash = Column(String)  # NFT minting transaction hash
    
    # Remove unique constraint to allow multiple attempts
    __table_args__ = ()
