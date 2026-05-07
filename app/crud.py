from datetime import timedelta
from sqlmodel import Session, select
from .models import User, Algorithm
from .auth import get_password_hash, verify_password, create_access_token


def create_user(session: Session, username: str, password: str) -> User:
    hashed = get_password_hash(password)
    user = User(username=username, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, username: str, password: str):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: User):
    data = {"sub": user.username}
    token = create_access_token(data)
    return token


def create_algorithm(session: Session, owner_id: int, **kwargs) -> Algorithm:
    alg = Algorithm(owner_id=owner_id, **kwargs)
    session.add(alg)
    session.commit()
    session.refresh(alg)
    return alg


def list_algorithms(session: Session):
    statement = select(Algorithm)
    return session.exec(statement).all()


def get_algorithm(session: Session, alg_id: int) -> Algorithm | None:
    statement = select(Algorithm).where(Algorithm.id == alg_id)
    return session.exec(statement).first()


def update_algorithm(session: Session, alg_id: int, **kwargs) -> Algorithm | None:
    alg = get_algorithm(session, alg_id)
    if not alg:
        return None
    for k, v in kwargs.items():
        if v is not None and hasattr(alg, k):
            setattr(alg, k, v)
    session.add(alg)
    session.commit()
    session.refresh(alg)
    return alg


def delete_algorithm(session: Session, alg_id: int) -> bool:
    alg = get_algorithm(session, alg_id)
    if not alg:
        return False
    session.delete(alg)
    session.commit()
    return True


def get_user(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


def list_users(session: Session):
    statement = select(User)
    return session.exec(statement).all()
