from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    course_id: int

class TransactionResult(BaseModel):
    transaction_id: str
    status: str
