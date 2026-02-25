from typing import List
from fastapi import Depends, HTTPException, status
from auth.oauth2 import get_current_user_roles


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user_roles: list = Depends(get_current_user_roles)):
        for role in current_user_roles:
            if role.role_name in self.allowed_roles:
                return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập cần thiết",
        )
