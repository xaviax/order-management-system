from rest_framework.permissions import BasePermission

class IsAccessingMenuItem(BasePermission):

        def has_permission(self,request,view):
            if request.method in ('GET','HEAD','OPTIONS'):
                return True

            return request.user.groups.filter(name="Manager").exists()





class IsManager(BasePermission):

    def has_permission(self,request,view):

        return request.user and request.user.groups.filter(name="Manager").exists()


class IsCustomer(BasePermission):

    def has_permission(self,request,view):

        return request.user and request.user.groups.filter(name="Customer").exists()

