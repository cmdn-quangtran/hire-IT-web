from rest_framework.permissions import BasePermission


class IsEmployeePermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role == 1:
                return True
            return False
        except Exception:
            print(str(Exception))
            return False
        
class IsRecruiterermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role == 2:
                return True
            return False
        except Exception:
            print(str(Exception))
            return False