from rest_framework import permissions

class IsAppointmentDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to modify their own appointments.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the authenticated user is the doctor assigned to this appointment
        return obj.doctor == request.user 