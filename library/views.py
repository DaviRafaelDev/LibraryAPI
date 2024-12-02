from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Reader, Loan
from .serializers import (
    BookSerializer, ReaderSerializer, LoanSerializer,
    RegisterSerializer, ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]


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


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    reader = request.user.reader

    if request.method == 'GET':
        serializer = ReaderSerializer(reader)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ReaderSerializer(reader, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out."})
    except Exception:
        return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
    parser_classes = [MultiPartParser, FormParser]


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()
        reader = Reader.objects.get(user=request.user)
        active_loans = Loan.objects.filter(reader=reader, returned=False).count()

        if active_loans >= 3:
            return Response({"error": "Maximum number of loans reached"}, status=status.HTTP_400_BAD_REQUEST)

        book_id = mutable_data.get('book')
        try:
            book = Book.objects.get(pk=book_id)
            if not book.is_available:
                return Response({"error": "Book is not available for loan"}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        mutable_data['reader'] = reader.id
        mutable_data['return_date'] = (timezone.now() + timezone.timedelta(days=14)).isoformat()
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        book.is_available = False
        book.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if loan.reader.user != request.user:
            return Response({"error": "You are not authorized to return this book"}, status=status.HTTP_403_FORBIDDEN)

        loan.returned = True
        loan.actual_return_date = timezone.now()
        loan.save()

        book = loan.book
        book.is_available = True
        book.save()

        return Response({'status': 'book returned'})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        reader = Reader.objects.get(user=request.user)
        pending_loans = Loan.objects.filter(
            reader=reader,
            returned=False,
            return_date__lt=timezone.now()
        )
        serializer = self.get_serializer(pending_loans, many=True)
        return Response(serializer.data)
