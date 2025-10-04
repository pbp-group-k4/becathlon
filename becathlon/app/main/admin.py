from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description_summary')
	search_fields = ('name',)

	def description_summary(self, obj):
		return (obj.description[:60] + '…') if obj.description and len(obj.description) > 60 else obj.description

	description_summary.short_description = 'Description'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'price', 'created_at')
	list_filter = ('category',)
	search_fields = ('name', 'category__name')
	autocomplete_fields = ('category',)
