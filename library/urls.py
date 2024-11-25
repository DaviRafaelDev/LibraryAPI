# library/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    BookViewSet, ReaderViewSet, LoanViewSet,
    RegisterView, ChangePasswordView,
    get_user_profile, logout_view
)

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'readers', ReaderViewSet)
router.register(r'loans', LoanViewSet)

urlpatterns = [
    # Rotas de autenticação
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/profile/', get_user_profile, name='user_profile'),
    path('auth/logout/', logout_view, name='logout'),
    
    # URLs geradas pelo router
    path('', include(router.urls)),
]