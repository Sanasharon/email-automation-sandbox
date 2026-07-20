# Permissions enum used by the admin RBAC system
# Each key is an internal action identifier; the corresponding value is a string
# that can be stored in the UserRole.permissions_json array.

PERMISSIONS = {
    # Users module
    "view_users": "users:view",
    "create_users": "users:create",
    "update_users": "users:update",
    "delete_users": "users:delete",
    "activate_user": "users:activate",
    "deactivate_user": "users:deactivate",
    "reset_password": "users:reset_password",
    "assign_role": "users:assign_role",
    # Roles module (new)
    "view_roles": "roles:view",
    "create_roles": "roles:create",
    "update_roles": "roles:update",
    "delete_roles": "roles:delete",
    "clone_role": "roles:clone",
    # Additional future modules can be added here following the same pattern
}

# Helper to expose a flat list of permission strings for UI dropdowns
def all_permission_strings() -> list[str]:
    return list(PERMISSIONS.values())
