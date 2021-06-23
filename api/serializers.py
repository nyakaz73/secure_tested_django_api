from rest_framework import serializers
from business.models import Customer


#https://stackoverflow.com/questions/28945327/django-rest-framework-with-choicefield
class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data) 


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    gender = ChoiceField(Customer.GENDER_CHOICES)

    def get_full_name(self,obj):
        return "{} {}".format(obj.name, obj.last_name)
    
    class Meta:
        model = Customer
        fields = ['id', 'full_name','title', 'gender', 'created']