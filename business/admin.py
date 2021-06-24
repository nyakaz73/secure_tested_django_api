from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_name','gender', 'status', 'created_by', 'created',)
    readonly_fields = ('created', )

    def full_name(self, obj):
        return obj.name + " " +obj.last_name

admin.site.register(Customer,CustomerAdmin)