from django.contrib import admin

# Register your models here.


class GuildMaterialStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock', 'unit')
    readonly_fields = ('stock', 'unit')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return ()


class GuildMaterialJournalAdmin(admin.ModelAdmin):
    list_display = (
        'material_input', 'amount_input', 'input_from', 'material_output', 'amount_output', 'output_to', 'comment'
    )

    def delete_queryset(self, request, queryset):
        # delete it one by one, to trigger model's delete method.
        for obj in queryset:
            obj.delete()
