from sqlalchemy.orm import Session

from app.models import FunctionalityAccess, User


def get_user_roles(session: Session, user: User):
    try:
        if user.role == 1:
            roles =  session.query(FunctionalityAccess).all()
            role_names = [role.name for role in roles if role.name]
            return role_names

        functionality_roles = user.functionality_roles
        if not functionality_roles:
            return []
        roles = session.query(FunctionalityAccess).filter(FunctionalityAccess.id.in_(functionality_roles)).all()
        role_names = [role.name for role in roles if role.name]
        return role_names

    except Exception as e:
        print(f"Error: {e}")
        return []


def has_role_access(session: Session, user: User, rolename):
    try:
        if not isinstance(rolename,str) or not rolename.strip():
            return False

        if not user:
            return False
        elif user.role == 1:
            return True
        elif user.functionality_roles is None:
            return False

        user_roles = get_user_roles(session, user)
        if rolename in user_roles:
            return True

        return False

    except Exception as e:
        print(f"Error: {e}")
        return False