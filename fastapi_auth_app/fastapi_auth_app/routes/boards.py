from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])

@router.post("/", response_model=schemas.ShowBoardWithRole)
def create_board(
    board: schemas.BoardCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    # 1️⃣ Create the board
    new_board = models.Board(name=board.name, owner_id=user.id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    # 2️⃣ Add the user as a board member with role = 'owner'
    new_member = models.BoardMember(board_id=new_board.id, user_id=user.id, role="owner")
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # 3️⃣ Return both board info + role
    return {
        "id": new_board.id,
        "name": new_board.name,
        "role": new_member.role
    }


@router.get("/", response_model=list[schemas.ShowBoard])
def get_boards(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Board).filter(models.Board.owner_id == user.id).all()
