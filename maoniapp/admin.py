import json
from django.contrib import admin
from django.http import HttpResponse
from .models.report import Report
from .models.business import Business, Code
from .models.slide import Slide
from .models.category import Category
from .models.review import Review
from .models.user import User, UserBusiness
from .models.comment import Comment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.banner import Banner
from .models.language import Language, Translation
from .models.code import Code
from django.contrib import admin
from .models import Business

class UserBusinessInline(admin.TabularInline):
    model = UserBusiness
    extra = 1  # Number of empty forms to show for adding new relationships
    verbose_name = "User Business"
    verbose_name_plural = "User Businesses"

# Custom admin for User
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at')
    # Fields to filter by in the admin interface
    list_filter = ('role', 'is_active', 'is_staff')
    # Searchable fields
    search_fields = ('email',)
    # Ordering by email
    ordering = ('email',)
    # Fields to show in the detail view of a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'role')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    # Fields to include when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')
    # Inline management for the ManyToMany relationship
    inlines = [UserBusinessInline]

def export_translations(modeladmin, request, queryset):
    # Récupérer les traductions sélectionnées ou toutes les traductions si aucune sélectionnée
    translations = queryset.all()

    # Créer une liste des traductions au format dict
    data = []
    for translation in translations:
        data.append({
            'language': translation.language.code,  # Assurez-vous d'ajuster en fonction de vos relations
            'key': translation.key,
            'value': translation.value
        })

    # Convertir les données en JSON
    json_data = json.dumps(data, indent=4)

    # Créer une réponse HTTP avec le type de contenu JSON
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="translations.json"'
    
    return response

export_translations.short_description = "Export selected translations to JSON"

class TranslationAdmin(admin.ModelAdmin):
    list_display = ['key', 'language', 'value']
    actions = [export_translations]  # Ajouter
    
class CodeInline(admin.TabularInline):
    model = Code
    extra = 0
    readonly_fields = ['invitation_code', 'is_active', 'created_at', 'updated_at']

class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name','country', 'city', 'category', 'get_codes_count']
    inlines = [CodeInline]

    def get_codes_count(self, obj):
        return obj.businesscodes.count()  # Nombre de codes associés à cette entreprise
    get_codes_count.short_description = 'Number of Codes'

class CodeAdmin(admin.ModelAdmin):
    list_display = ['invitation_code', 'business', 'is_active', 'created_at', 'updated_at']
    search_fields = ['invitation_code', 'business__name']
    list_filter = ['is_active', 'business']

# Register models in admin
admin.site.register(User, UserAdmin)
admin.site.register(UserBusiness)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Slide)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Banner)
admin.site.register(Report)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(Language)
admin.site.register(Code, CodeAdmin)

