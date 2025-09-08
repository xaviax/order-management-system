from django.shortcuts import render
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics, filters
from .serializers import *
from .models import *
from .permissions import *
from django.contrib.auth.models import Group
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
# Create your views here.


class MenuItemListView(generics.ListCreateAPIView):
    queryset=MenuItem.objects.all()
    serializer_class=MenuItemSerializer
    permission_classes = [IsAccessingMenuItem]
    filter_backends =[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]

    #field filtering
    filterset_fields=['price','category']

   #text search
    search_fields=['title']




    ordering_fields=['price','title']
   #this below is the default ordering
    ordering =['id']


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAccessingMenuItem]


class UserGroupManager(generics.ListCreateAPIView):

    serializer_class = UserSerializer
    permission_classes =[IsAuthenticated,IsManager]

    def get_queryset(self):

        return User.objects.filter(groups__name="Manager").prefetch_related('groups')


    def get_serializer_class(self):

        if self.request.method =='POST':
            return UserGroupAssignSerializer

        return UserSerializer


    def perform_create(self,serializer):

        username=serializer.validated_data['username']
        user = User.objects.get(username=username)
        manager_group = Group.objects.get(name='Manager')
        user.groups.add(manager_group)



class ManagerDestroy(generics.DestroyAPIView):
    queryset=User.objects.all()
    permission_classes=[IsAuthenticated,IsManager]


    def perform_destroy(self,instance):

        manager_group=Group.objects.get(name='Manager')

        if instance.groups.filter(name='Manager').exists():
            instance.groups.remove(manager_group)

        else:
            raise ValidationError("User in not a Manager")



class DeliveryCrewListCreate(generics.ListCreateAPIView):
        queryset=User.objects.all()
        serializer_class=UserSerializer
        permission_classes=[IsAuthenticated,IsManager]

        def get_queryset(self):
            return User.objects.filter(groups__name='Delivery Crew').prefetch_related('groups')

        def get_serializer_class(self):
            if self.request.method =='POST':
                return UserGroupAssignDeliveryCrewSerializer

            return UserSerializer

        def perform_create(self,serializer):
            username=serializer.validated_data['username']
            user= User.objects.get(username=username)
            delivery_crew_group = Group.objects.get(name='Delivery Crew')
            user.groups.add(delivery_crew_group)





class DeliveryCrewDestroy(generics.DestroyAPIView):

    queryset=User.objects.all()
    permission_classes=[IsAuthenticated,IsManager]

    def perform_destroy(self,instance):

        delivery_crew_group=Group.objects.get(name='Delivery Crew')
        if instance.groups.filter(name='Delivery Crew').exists:
            instance.groups.remove(delivery_crew_group)

        elif instance.groups.exists() is not True:
            raise ValidationError('User does not belong to Delivery Group')



class CartListCreateDelete(generics.ListCreateAPIView):

    serializer_class=CartSerializer
    permission_classes =[IsAuthenticated,IsCustomer]

    def get_queryset(self):

        return Cart.objects.filter(user=self.request.user)

    def delete(self,request):
        Cart.objects.filter(user=self.request.user).delete()
        return Response({'message': 'Cart emptied!!'}, status=204)



class OrderCreateList(generics.ListCreateAPIView):

    serializer_class=OrderSerializer
    permission_classes=[IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]

    filterset_fields=['status','total','date']



    ordering_fields=['date','total']

    ordering =['-date']



    def get_queryset(self):

        current_user=self.request.user

        if self.request.user.groups.filter(name='Customer').exists():

            return Order.objects.filter(user=current_user)

        elif self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()

        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=current_user)


        return Order.objects.none()

    def perform_create(self,serializer):
        user=self.request.user
        cart_items=Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise ValidationError("Cart is Empty")



        with transaction.atomic():

            total = sum([item.price for item in cart_items])
            order = serializer.save(user=user,total=total)

            order_items=[
                OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    unit_price=item.unit_price,
                    price=item.price,
                    quantity=item.quantity
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(user=user).delete()





class OrderRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    serializer_class=OrderSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):

        user=self.request.user

        if self.request.user.groups.filter(name='Customer').exists():
            return Order.objects.filter(user=user)

        elif self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()

        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.none()


    def perform_update(self,serializer):
        user = self.request.user
        if  user.groups.filter(name='Manager').exists():
            #the required data from the manager will be the id for the delivery crew and nothing else
            delivery_crew=self.request.data.get("delivery_crew")

            if not delivery_crew:
                raise ValidationError({"delivery_crew":"This field is required"})

            serializer.save(delivery_crew_id=delivery_crew)


        elif user.groups.filter(name='Delivery Crew').exists():
            status=self.request.data.get("status")

            if not status:
                raise ValidationError({'status':'This field is required'})

            status_value=str(status).lower()
            normalized_status_value=None

            if status_value in ['1','true']:
                normalized_status_value=True

            elif status_value in ['0','false']:
                normalized_status_value=False

            else:
                raise ValidationError({'status':'must be boolean or true/false'})

            serializer.save(status=normalized_status_value)


        else:
            raise PermissionDenied("You do not have permission to make changes")

    def perform_destroy(self,instance):
        user= self.request.user

        if user.groups.filter(name='Manager').exists():
          instance.delete()

        else:
            raise PermissionDenied("You do not have the permission to delete order")

















