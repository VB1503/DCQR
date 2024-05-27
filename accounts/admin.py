from django.contrib import admin
from .models import User, BusinessUser, Category, BusinessDetails,QRModel
from django.utils.html import format_html




@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['image_tag','phone_number','first_name','last_name','email','id']
    search_fields = ['first_name','last_name','phone_number','email']
    list_filter = ['is_active','is_business_user', 'is_verified','auth_provider']
    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:30px; max-height:30px; border-radius: 50%; object-fit: cover;"/>'.format(obj.profile_pic))

    image_tag.short_description = 'Profile'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'parent', 'display_category_image')
    list_filter = ('parent',)
    search_fields = ('category',)
    ordering = ('tree_id', 'level', 'category')
    readonly_fields = ('id',)

    def display_category_image(self, obj):
        return format_html('<a href="{0}" class="button" target="_blank">Profile Link</a>&nbsp;', obj.categoryImage)

    display_category_image.allow_tags = True
    display_category_image.short_description = 'Category Image'

admin.site.register(Category, CategoryAdmin)

@admin.register(BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    list_display = ['user','full_name','phone_number','priority']
    search_fields = ['full_name','phone_number','priority']
    list_filter = ['priority']

@admin.register(BusinessDetails)
class BusinessDetailsAdmin(admin.ModelAdmin):
    list_display = ['business_user','image_tag','business_name','business_phone_number','business_email','business_id','category']
    search_fields = ['business_user__phone_number','business_name','business_phone_number','business_email','business_id']
    list_filter=['rating']
    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:30px; max-height:30px; border-radius: 50%; object-fit: cover;"/>'.format(obj.business_profile))

    image_tag.short_description = 'Profile'

@admin.register(QRModel)
class QRAdmin(admin.ModelAdmin):
    list_display = ['qr_link','qr_redirect_link','business_phone_number','business_name']
    search_fields = ['business_phone_number','business_name','business_email','business_id']

