from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow full access to admin users, read-only for others."""

    def has_permission(self, request, view):
        # Safe methods are allowed for anyone (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # For write methods require authenticated staff
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AllowAuthenticatedNonAdminOrReadOnly(permissions.BasePermission):
    """Allow read for anyone, allow writes only for authenticated non-admin users.

    Use this for carts and cart-items: admins may inspect but cannot add/update carts/orders.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # write methods require authentication and NOT staff
        return bool(request.user and request.user.is_authenticated and not request.user.is_staff)


class OrderPermissionForAdminAndOwner(permissions.BasePermission):
    """Custom permission for Pedido:
    - SAFE_METHODS: allow for anyone
    - POST: allow authenticated non-admins (buyers) to create orders
    - PATCH/PUT: allow admins to update order status, and owners to view/update limited fields
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated and not request.user.is_staff)
        # For other write methods (PATCH/PUT/DELETE) allow authenticated users (detail-level checks will apply)
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # SAFE methods already allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admins can modify (change status)
        if request.user and request.user.is_staff:
            return True
        # Owners (the user who created the order) can view and may update limited fields
        try:
            is_owner = obj.usuario == request.user
        except Exception:
            is_owner = False
        # Owners can delete or modify their own orders (depending on business rules); allow for now
        if is_owner:
            return True
        return False
