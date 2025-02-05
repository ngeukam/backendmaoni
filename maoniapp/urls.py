from django.urls import path, include

from .controllers.translationcontroller import TranslationView

from .controllers.reportcontroller import UserBusinessReportListView

from .controllers.bannercontroller import BannerViewSet

from .controllers.slidecontroller import SlideViewSet

from .controllers.codecontroller import CheckCodeStatusView

from .controllers.commentcontroller import CreateCommentView

from .controllers.businesscontroller import (
    BusinessListCreateView, BusinessListNameView, BusinessListView, BusinessRetrieveUpdateView, BusinessDetailView, ChangeUserBusinessView, DeleteUserBusinessView, FilterBusinessReviewsByNameView, 
    RelatedBusinessesView, BusinessWithReviewsListView, GetAllBusinessByCategory, UserBusinessReviews, UserBusinessesView, UsersInSameBusinessView, BusinessBrandListView
)
from .controllers.categorycontroller import (
    CategoryBusinessCountView, CategoryListCreateView, CategoryRetrieveUpdateDeleteView, FilterCategoryWithNameView
)
from .controllers.reviewcontroller import (
    ReviewCommentsView, ReviewListCreateView, ReviewListByBusinessView, ReviewUpdateView
)
from .controllers.authcontroller import (CheckSessionView, SignupView, LoginView, LogoutView, CreateCollaboratorView, ChangePasswordView)
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'slides', SlideViewSet, basename='slide')
router.register(r'banners', BannerViewSet, basename='banner')

urlpatterns = [
    path('', include(router.urls)),

    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('businesses/', BusinessListCreateView.as_view(), name='business-list-create'),
    path('business/<uuid:pk>/', BusinessRetrieveUpdateView.as_view(), name='business-retrieve-update'),
    
    path('businessnames/', BusinessListNameView.as_view(), name='business-list-name'),
    path('business-with-reviews/', BusinessWithReviewsListView.as_view(), name='business-with-reviews'),
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('category-business-count/', CategoryBusinessCountView.as_view(), name='category-business-count'),
    path('categories/<uuid:pk>/', CategoryRetrieveUpdateDeleteView.as_view(), name='category-detail'),
    path('filtercategoryname/', FilterCategoryWithNameView.as_view(), name='filter-category-by-name'),
    
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('deletereview/<uuid:reviewId>/', ReviewUpdateView.as_view(), name='update-review'),
    
    path('businessdetails/', BusinessDetailView.as_view(), name='business-detail'),
    path('business-reviews-list/', ReviewListByBusinessView.as_view(), name='business-reviews'),
    path('filter-business-reviews-by-name/', FilterBusinessReviewsByNameView.as_view(), name='filter-business-reviews-by-name'),
    path('business/<uuid:business_id>/related/', RelatedBusinessesView.as_view(), name='related-businesses'),
    path('businessesbrand/', BusinessBrandListView.as_view(), name='businesses-brand'),
    
    path('create-comment/<uuid:review_id>/review/', CreateCommentView.as_view(), name='create-comment'),
    path('reviews/<uuid:review_id>/comments/', ReviewCommentsView.as_view(), name='review-comments'),
    
    path('businesses-by-category/<str:categoryName>/', GetAllBusinessByCategory.as_view(), name='businesses-by-category'),
    path('create-collaborator/', CreateCollaboratorView.as_view(), name='create-collaborator'),
    
    path('user-businesses/', UserBusinessesView.as_view(), name='user-businesses'),
    path('user/reviews/', UserBusinessReviews.as_view(), name='user-business-reviews'),
     
    path('users/same-business/', UsersInSameBusinessView.as_view(), name='users-same-business'),
    path('change-business/<uuid:user_id>/', ChangeUserBusinessView.as_view(), name='change-user-business'),
     
    path('delete-user-business/<uuid:user_id>/<uuid:business_id>/', DeleteUserBusinessView.as_view(), name='delete_user_business'),
     
    path('check-session/', CheckSessionView.as_view(), name='check-session'),
      
    path('check-code-status/<str:invitation_code>/', CheckCodeStatusView.as_view(), name='check-code-status'),
    
    path('reports/', UserBusinessReportListView.as_view(), name='user-reports-list'),
     
    path('filter-businesses/', BusinessListView.as_view(), name='business-by-filter-list'),
    
    path('translations/', TranslationView.as_view(), name='translations'),
    
]   
