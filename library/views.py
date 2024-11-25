# library/views.py

from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Book, Reader, Loan
from .serializers import (
    BookSerializer, ReaderSerializer, LoanSerializer,
    RegisterSerializer, UserSerializer, ChangePasswordSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data.get("old_password")):
            return Response(
                {"old_password": ["Wrong password."]}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response({"message": "Password updated successfully"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out."})
    except Exception:
        return Response({"message": "Invalid token."}, status=400)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def most_borrowed(self, request):
        books = Book.objects.annotate(
            loan_count=models.Count('loan')
        ).order_by('-loan_count')[:10]
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

class ReaderViewSet(viewsets.ModelViewSet):
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        reader = Reader.objects.get(pk=request.data['reader'])
        active_loans = Loan.objects.filter(
            reader=reader,
            returned=False
        ).count()
        
        if active_loans >= 3:
            return Response(
                {"error": "Maximum number of loans reached"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        loan.returned = True
        loan.actual_return_date = timezone.now()
        loan.save()
        return Response({'status': 'book returned'})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending_loans = Loan.objects.filter(
            returned=False,
            return_date__lt=timezone.now()
        )
        serializer = self.get_serializer(pending_loans, many=True)
        return Response(serializer.data)