from rest_framework.permissions import BasePermission

class IsEnrolled(BasePermission):
#subclass BasePermission class and override the has_object_permission
 def has_object_permission(self, request, view, obj):
    return obj.students.filter(id=request.user.id).exists()    