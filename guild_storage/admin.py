from django.contrib import admin

# Register your models here.


class GuildMaterialStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock', 'unit')
    readonly_fields = ('stock', 'unit')


class GuildMaterialJournalAdmin(admin.ModelAdmin):
    list_display = (
        'material_input', 'amount_input', 'input_from', 'material_output', 'amount_output', 'output_to', 'comment'
    )
