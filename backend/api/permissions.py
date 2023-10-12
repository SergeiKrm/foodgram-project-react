from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
    
'''
class AnonOrMe(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS
                and request.path == '/api/users/me/'
                and not request.user.is_authenticated):
            return False
        if (request.method in permissions.SAFE_METHODS
                and request.path == '/api/users/me/'
                and request.user.is_authenticated):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
'''