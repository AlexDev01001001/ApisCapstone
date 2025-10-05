from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrganizerOrReadOnly(BasePermission):
    """
    Lectura para todos. Escribir solo si el request.user es el organizer_user o es staff.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return (getattr(obj, "organizer_user_id", None) == request.user.id) or request.user.is_staff
