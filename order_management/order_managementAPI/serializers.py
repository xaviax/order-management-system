from rest_framework import serializers
from .models import *


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields='__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','groups']


# The code below is a plain serializer for adding
# an already existing user to a group

class UserGroupAssignSerializer(serializers.Serializer):

    username = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )

    def validate_username(self,value):



        if value.groups.exists() :
            raise serializers.ValidationError("User already belongs to some group")

        return value



class UserGroupRemovalSerializer(serializers.Serializer):

    username = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )

    def validate_username(self,value):

        if value.groups.filter(name='Manager').exists() is not True:

            raise serializers.ValidationError("User is not a Manager")

        return value


class UserGroupAssignDeliveryCrewSerializer(serializers.Serializer):

        username=serializers.SlugRelatedField(
            queryset=User.objects.all(), slug_field='username'
        )

        def validate_username(self,value):

            if value.groups.exists():
                raise serializers.ValidationError('User already belongs to a Group')

            return value


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model=Cart
        fields=['menuitem','quantity']

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']

        unit_price = menuitem.price
        total_price = unit_price * quantity

        return Cart.objects.create(

            user=user,
            menuitem=menuitem,
            unit_price=unit_price,
            price=total_price,
            quantity=quantity
        )



class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'






class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields='__all__'



