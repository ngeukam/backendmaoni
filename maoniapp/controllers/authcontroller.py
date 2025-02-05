from django.contrib.sessions.models import Session
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from ..models.user import UserBusiness
from ..models.business import Business
from .serializers import BusinessSerializer, SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from ..permissions.permissions import IsAdminRole
from django.utils.timezone import now
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get("user", {})
        business_data = request.data.get("business", {})

        if not business_data:
            return Response({"error": "Business data is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate business
        business_exists = Business.objects.filter(
            name=business_data.get("name"),
            category_id=business_data.get("category"),
            country=business_data.get("country"),
            city=business_data.get("city"),
        ).exists()

        if business_exists:
            return Response({"error": "A business with the same name, category, country, and city already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Serialize and validate user data
        user_serializer = SignupSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Serialize and validate business data
        business_serializer = BusinessSerializer(data=business_data)
        if not business_serializer.is_valid():
            return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create user and business in a transaction
        with transaction.atomic():
            # Save the business first
            business = business_serializer.save()

            # Save the user and associate with the business
            user = user_serializer.save()
            user.businesses.add(business)
            # Créer un token JWT pour l'utilisateur
            refresh = RefreshToken.for_user(user)
            # Vérifier si une session est déjà active pour cet utilisateur
            if user.current_session_key and Session.objects.filter(pk=user.current_session_key).exists():
                 return Response(
                    {
                        "message": "A session is already active for this user.",
                        "session_active": True,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Enregistrer la nouvelle session active
            if not request.session.session_key:
                request.session.create()
            user.current_session_key = request.session.session_key
            user.save()
            
            # Vérifier si l'utilisateur est actif dans UserBusiness
            user_business = UserBusiness.objects.filter(user=user, business=business).first()
            is_active = user_business.is_active if user_business else False

        # Créer les données de réponse avec les tokens JWT
        response_data = {
            "_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "business_id": str(business.id),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "is_active": is_active,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    
class CreateCollaboratorView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    def post(self, request):
        # Extract business_ids from request data
        business_ids = request.data.get('business_ids', [])
        # Validate that the business_ids exist and are valid
        if business_ids:
            businesses = Business.objects.filter(id__in=business_ids)

            if len(businesses) != len(business_ids):
                return Response({"error": "One or more business IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            businesses = []
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Associate the user with the provided businesses
            user.businesses.set(businesses)  # Set the businesses many-to-many field
            user.save()

            # Construct the response with the necessary user info and tokens
            response_data = {
                '_id': str(user.id),  # Include user ID
                'email': user.email,  # Include email
                'role': user.role,  # Include role
                'business_ids': business_ids,  # Include business IDs provided by frontend
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Vérifier si une session est déjà active pour cet utilisateur
            if hasattr(user, 'current_session_key') and user.current_session_key:  # Check if attribute exists
                try:
                    existing_session = Session.objects.get(pk=user.current_session_key)
                    if existing_session.expire_date > now():  # Check if session is still valid
                        return Response(
                            {
                                "message": "A session is already active for this user.",
                                "session_active": True,  # Indicate that a session is active
                            },
                            status=status.HTTP_400_BAD_REQUEST,  # Or another appropriate status code
                        )
                    else: # Session expired, clear it
                        existing_session.delete()
                        user.current_session_key = None # Clear the key
                        user.save()

                except Session.DoesNotExist:
                    user.current_session_key = None # Clear the key if the session doesn't exist
                    user.save()
                    pass  # Si la session n'existe plus, on continue


            # Créer un token JWT pour l'utilisateur connecté
            refresh = RefreshToken.for_user(user)

            # Créer une nouvelle session pour l'utilisateur
            if not request.session.session_key:
                request.session.create()
            user.current_session_key = request.session.session_key
            user.save()

            # ... (rest of your code for business_data and response)

            business_data = []
            for business in user.businesses.all():
                user_business = UserBusiness.objects.filter(user=user, business=business).first()
                is_active = user_business.is_active if user_business else False
                business_data.append({
                    "business_id": str(business.id),
                    "is_active": is_active
                })

            response_data = {
                '_id': str(user.id),
                'email': user.email,
                'role': user.role,
                'business_data': business_data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }

            return Response(
                {
                    "message": "Login successfully!",
                    "data": response_data,
                    "session_active": False, # Indicate that a new session was created
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Blacklist the refresh token (more reliable than relying on request.auth directly)
            if hasattr(request.user, 'current_session_key') and request.user.current_session_key:  # Check attribute existence
                try:
                    refresh_token = request.data.get('refresh_token') # Get refresh token from request body
                    if refresh_token:
                        RefreshToken(refresh_token).blacklist()
                    else:
                        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
                except TokenError as e:
                    # Log the error for debugging, but don't necessarily fail the logout.
                    # The token might be invalid or expired, but we still want to clear the session.
                    print(f"Token blacklist error: {e}")  # Or use a proper logger
                    pass # Continue with logout even if blacklisting fails

                # Remove the user's session (always do this, even if token blacklisting fails)
                existing_session = Session.objects.get(pk=request.user.current_session_key)
                existing_session.delete()
                request.user.current_session_key = None # Clear the key
                request.user.save()

            else:
                return Response({"detail": "No active session found"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            # Handle the case where the session key is present but the session doesn't exist
            request.user.current_session_key = None
            request.user.save()
            return Response({"detail": "No active session found"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:  # Catch any other unexpected errors
            print(f"Logout error: {e}") # Log the error for debugging
            return Response({"detail": f"Logout failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract data from the request
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Validate the old password
        if not old_password or not authenticate(email=request.user.email, password=old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password and confirm password match
        if new_password != confirm_password:
            return Response({"error": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password using Django's password validators
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "Password updated successfully.", "error":False}, status=status.HTTP_200_OK)

class CheckSessionView(APIView):
    # Allow both authenticated and unauthenticated users
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # User is not authenticated
            return Response(
                {
                    "message": "User is not authenticated.",
                    "session_active": False,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # User is authenticated, proceed with session checking
        session_key = getattr(request.user, "current_session_key", None)
        if session_key and Session.objects.filter(pk=session_key).exists():
            session = Session.objects.get(pk=session_key)

            # Check if the session is still active
            if session.expire_date > now():
                return Response(
                    {
                        "message": "Session is active.",
                        "session_active": True,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Session expired: Logout user and clear session key
                logout(request)
                request.user.current_session_key = None

                # Only save if the user is authenticated, not an anonymous user
                if not isinstance(request.user, AnonymousUser):
                    request.user.save()

                return Response(
                    {
                        "message": "Session has expired. User logged out.",
                        "session_active": False,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        return Response(
            {
                "message": "No active session found.",
                "session_active": False,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
