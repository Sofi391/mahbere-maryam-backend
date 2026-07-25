from rest_framework.permissions import BasePermission


class IsStaffAndAuthenticated(BasePermission):
    """
    Grants access only to users who are both authenticated and marked as staff.
    Use this for all admin/committee write operations.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
