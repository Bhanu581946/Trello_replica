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


@router.get("/owned", response_model=list[schemas.ShowBoard])
def get_boards(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Board).filter(models.Board.owner_id == user.id).all()

@router.get("/all", response_model=list[schemas.ShowBoardWithRole])
def get_boards(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    # Join BoardMember table to include boards where user is a member
    boards = (
        db.query(models.Board, models.BoardMember.role)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(models.BoardMember.user_id == user.id)
        .all()
    )

    # Convert results into list of dicts
    result = [
        {"id": b.Board.id, "name": b.Board.name, "role": b.role}
        for b in boards
    ]
    return result


@router.post("/{board_id}/invite")
def invite_member(
    board_id: int,
    invite_data: schemas.InviteMember,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1️⃣ Check if board exists
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # 2️⃣ Check if current user is the board owner or admin
    member = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == current_user.id
        )
        .first()
    )
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="You are not allowed to invite members")

    # 3️⃣ Find the user to invite (by username or email)
    invited_user = (
        db.query(models.User)
        .filter(
            (models.User.username == invite_data.username_or_email) |
            (models.User.email == invite_data.username_or_email)
        )
        .first()
    )
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 4️⃣ Check if already a member
    existing_member = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == invited_user.id
        )
        .first()
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member")

    # 5️⃣ Add the user to board_members
    new_member = models.BoardMember(
        board_id=board_id,
        user_id=invited_user.id,
        role=invite.role 
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "message": f"{invited_user.username} has been added to the board successfully.",
        "board_id": board_id,
        "member_role": new_member.role
    }

