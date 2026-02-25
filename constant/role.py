from auth.permissions import RoleChecker


ADMIN_ROLE = RoleChecker(["admin"])
ALL_ROLE = RoleChecker(["admin", "member"])
