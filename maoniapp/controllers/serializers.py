from rest_framework import serializers
from django.contrib.auth import authenticate

from ..models.language import Language, Translation
from ..models.report import Report
from ..models.banner import Banner
from ..models.slide import Slide
from ..models.user import User, UserBusiness
from ..models.business import Business, Code
from ..models.category import Category
from ..models.review import Review
from ..models.comment import Comment
import pycountry

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'subcategories']
        read_only_fields = ['id']
    def get_subcategories(self, obj):
        # Recursively display all subcategories
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'id']  # Inclure uniquement les champs 'name id'
        read_only_fields = ['id']

#Display name and id Business
class BusinessDisplaysSerializer(serializers.ModelSerializer):
    countrynamecode = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)  # Nested Category Display
    active_codes = serializers.SerializerMethodField()
    inactive_codes = serializers.SerializerMethodField()
    logo = serializers.ImageField(required=False)
    total_evaluation = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ['id', 'name', 'city', 'country', 'total_evaluation', 'countrynamecode', 'logo', 'phone', 'description','showeval', 'showreview', 'btype', 'email', 'category', 'active', 'active_codes', 'inactive_codes']
        ordering = ('-created_at',)
        read_only_fields = ['id']
        extra_kwargs = {
            'city': {'required': False, 'allow_null': True},
            'country': {'required': False, 'allow_null': True},
            'name': {'required': False, 'allow_null': True},
        }
        
    def get_active_codes(self, obj):
        # Récupérer les codes actifs
        active_codes = Code.objects.filter(business=obj, is_active=True).values('invitation_code')
        return [code['invitation_code'] for code in active_codes]

    def get_inactive_codes(self, obj):
        # Récupérer les codes non actifs
        inactive_codes = Code.objects.filter(business=obj, is_active=False).values('invitation_code')
        return [code['invitation_code'] for code in inactive_codes]
    
    def get_countrynamecode(self, obj):
        # Utilisation de pycountry pour obtenir le nom du pays à partir du code
        try:
            country = pycountry.countries.get(alpha_2=obj.country)
            return country.name if country else None
        except KeyError:
            return None
    def get_total_evaluation(self, obj):
        return obj.get_reviews_info()['total_evaluation']

    def update(self, instance, validated_data):
        # Si un fichier est présent, vous devrez peut-être le gérer ici
        logo = validated_data.get('logo', None)
        if logo:
            # Si un nouveau logo est téléchargé, il sera associé à l'instance
            instance.logo = logo
        
        # Mettre à jour les autres champs
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.description = validated_data.get('description', instance.description)
        instance.btype = validated_data.get('btype', instance.btype)
        instance.showeval = validated_data.get('showeval', instance.showeval)
        instance.showreview = validated_data.get('showreview', instance.showreview)

        instance.save()
        return instance

class BusinessBrandDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model= Business
        fields = ['id', 'name', 'logo', 'website']

class UserDisplaySerializer(serializers.ModelSerializer):
    businesses = BusinessDisplaysSerializer(many=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'created_at', 'businesses']
        read_only_fields = ['id', 'created_at']
        
class UserBusinessSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
    
    class Meta:
        model = UserBusiness
        fields = ['user', 'business', 'is_active']

    def validate(self, data):
        # S'assurer qu'un utilisateur n'est lié qu'à une entreprise une seule fois
        if UserBusiness.objects.filter(user=data['user'], business=data['business']).exists():
            raise serializers.ValidationError("L'utilisateur est déjà associé à cette entreprise.")
        return data         

class BusinessSerializer(serializers.ModelSerializer):
    total_reviews = serializers.SerializerMethodField()
    total_evaluation = serializers.SerializerMethodField()
    has_reviews = serializers.SerializerMethodField()
    countrynamecode = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)  # Nested Category Display
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Business
        fields = [
            'id', 'name', 'logo', 'category', 'isverified', 'btype', 'category_id',
            'country', 'countrynamecode', 'city', 'website', 'phone', 'email', 'category_name',
            'description', 'showeval', 'showreview', 'updated_at', 'created_at', 'total_reviews',
            'total_evaluation', 'has_reviews'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True},
            'countrynamecode': {'required': False, 'allow_null': True},
        }

    def get_total_reviews(self, obj):
        return obj.get_reviews_info()['total_reviews']

    def get_total_evaluation(self, obj):
        return obj.get_reviews_info()['total_evaluation']

    def get_has_reviews(self, obj):
        return obj.get_reviews_info()['has_reviews']

    def get_countrynamecode(self, obj):
        try:
            country = pycountry.countries.get(alpha_2=obj.country)
            return country.name if country else None
        except KeyError:
            return None

    def create(self, validated_data):
        # Create a new Business instance with the validated data
        logo = validated_data.get('logo', None)
        if logo:
            validated_data['logo'] = logo

        # Create and return the new Business instance
        return Business.objects.create(**validated_data)

        
#Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'review', 'user', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
         
# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)  # Nested Business Display
    business_id = serializers.PrimaryKeyRelatedField(
        queryset=Business.objects.all(), source='business', write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Review
        fields = [
            'id', 'text', 'title', 'record', 'score', 'business', 'comments', 'evaluation', 'business_id', 'expdate',
            'sentiment', 'authorname', 'contact', 'active', 'authorcountry', 'latitude', 'longitude', 'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        instance.active = validated_data.get('active', instance.active)
        instance.save()
        return instance
        
# Sérialiseur pour l'inscription
class SignupSerializer(serializers.ModelSerializer):
    # Adding business_ids as a field to the serializer
    business_ids = serializers.ListField(
        child=serializers.UUIDField(),  # Expecting a list of UUIDs
        required=False,  # This field is optional for now
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'business_ids', 'is_active']  # Include the new field

    def create(self, validated_data):
        business_ids = validated_data.pop('business_ids', [])  # Extract business_ids if provided

        # Create the user instance without businesses
        user = User.objects.create_user(**validated_data)

        # If business_ids are provided, associate businesses with the user
        if business_ids:
            businesses = Business.objects.filter(id__in=business_ids)
            user.businesses.set(businesses)  # Assign the businesses to the user
            user.save()

        return user

    def validate_business_ids(self, value):
        # Validate that the business_ids provided exist in the database
        if value:
            businesses = Business.objects.filter(id__in=value)
            if len(businesses) != len(value):
                raise serializers.ValidationError("One or more business IDs are invalid.")
        return value

# Sérialiseur pour la connexion
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
            
        attrs['user'] = user
        return attrs

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ['id', 'invitation_code', 'business', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SlideSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class BannerSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CategoryBusinessCountSerializer(serializers.ModelSerializer):
    business_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'business_count', 'active']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__' 

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name']

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['key', 'value']

class TranslationResponseSerializer(serializers.Serializer):  # For the API response
    language = serializers.CharField()
    last_updated = serializers.DateTimeField() # Or just CharField if you don't need real date
    translations = TranslationSerializer(many=True, read_only=True)

    def to_representation(self, instance):  # Customize representation for nested data
      ret = super().to_representation(instance)
      ret['translations'] = {item['key']: item['value'] for item in ret['translations']}
      return ret