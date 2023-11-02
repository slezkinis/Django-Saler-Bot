from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name_ru', 'name_en']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter=['source']
    search_fields = ['name_ru', 'name_en']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'tg_id']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_filter=['product', 'is_enabled']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter=['user', 'account', 'status']


@admin.register(Setting)
class SettingsModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    search_fields=['name']