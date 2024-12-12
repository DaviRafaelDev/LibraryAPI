import pytest
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from library.models import Book, Loan, Reader


@pytest.mark.django_db
class TestAdminFunctionality:
    def setup_method(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@library.com', 
            password='AdminStr0ngP@ss2024!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_add_book(self):
        url = reverse('book-list')
        book_data = {
            'title': 'Python Mastery',
            'author': 'John Smith',
            'genre': 'Technology',
            'publication_year': 2024
        }
        response = self.client.post(url, book_data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == 1
        assert Book.objects.first().title == 'Python Mastery'

    def test_update_book(self):
        book = Book.objects.create(
            title='Old Book Title', 
            author='Old Author', 
            genre='Outdated', 
            publication_year=2000
        )
        url = reverse('book-detail', kwargs={'pk': book.id})
        update_data = {
            'title': 'Updated Book Title',
            'author': 'Updated Author',
            'genre': 'Updated Genre',
            'publication_year': 2024
        }
        response = self.client.put(url, update_data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == 'Updated Book Title'
        assert book.publication_year == 2024

    def test_delete_book(self):
        book = Book.objects.create(
            title='Book to Delete', 
            author='Deletion Test', 
            genre='Test', 
            publication_year=2024
        )
        url = reverse('book-detail', kwargs={'pk': book.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.count() == 0

    def test_list_most_borrowed_books(self):
        book1 = Book.objects.create(
            title='Most Popular', 
            author='Top Author', 
            genre='Popular', 
            publication_year=2024
        )
        book2 = Book.objects.create(
            title='Less Popular', 
            author='Another Author', 
            genre='Random', 
            publication_year=2023
        )
        reader = Reader.objects.create(
            user=User.objects.create_user(
                username='borrower', 
                password='TestP@ss2024!'
            ),
            address='Test Address',
            phone='1234567890'
        )
        for _ in range(3):
            Loan.objects.create(
                book=book1, 
                reader=reader, 
                return_date=timezone.now() + timezone.timedelta(days=14)
            )
        url = reverse('book-most-borrowed')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert response.data[0]['title'] == 'Most Popular'

    def test_monitor_active_loans(self):
        book1 = Book.objects.create(
            title='Borrowed Book 1', 
            author='Author 1', 
            genre='Fiction', 
            publication_year=2024
        )
        book2 = Book.objects.create(
            title='Borrowed Book 2', 
            author='Author 2', 
            genre='Non-Fiction', 
            publication_year=2023
        )
        reader = Reader.objects.create(
            user=User.objects.create_user(
                username='active_borrower', 
                password='TestP@ss2024!'
            ),
            address='Test Address',
            phone='1234567890'
        )
        Loan.objects.create(
            book=book1, 
            reader=reader, 
            return_date=timezone.now() + timezone.timedelta(days=14)
        )
        Loan.objects.create(
            book=book2, 
            reader=reader, 
            return_date=timezone.now() + timezone.timedelta(days=14)
        )
        url = reverse('loan-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestUserFunctionality:
    def setup_method(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='UserStr0ngP@ss2024!'
        )
        self.reader = Reader.objects.create(
            user=self.user, 
            address='123 Test Street', 
            phone='9876543210'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        self.client.logout()
        url = reverse('register')
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewStr0ngP@ss2024!',
            'password2': 'NewStr0ngP@ss2024!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, registration_data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()

    def test_user_profile_management(self):
        url = reverse('user_profile')
        get_response = self.client.get(url)
        assert get_response.status_code == status.HTTP_200_OK
        update_data = {
            'address': 'Updated Address 456',
            'phone': '5555555555'
        }
        put_response = self.client.put(url, update_data, format='json')
        assert put_response.status_code == status.HTTP_200_OK
        self.reader.refresh_from_db()
        assert self.reader.address == 'Updated Address 456'

    def test_book_loan_workflow(self):
        book = Book.objects.create(
            title='Test Book', 
            author='Test Author', 
            genre='Test Genre', 
            publication_year=2024,
            is_available=True
        )
        loan_url = reverse('loan-list')
        loan_data = {'book': book.id}
        loan_response = self.client.post(loan_url, loan_data, format='json')
        assert loan_response.status_code == status.HTTP_201_CREATED
        book.refresh_from_db()
        assert not book.is_available
        loan = Loan.objects.first()
        return_url = reverse('loan-return-book', kwargs={'pk': loan.id})
        return_response = self.client.post(return_url, format='json')
        assert return_response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.is_available

    def test_loan_limit_enforcement(self):
        books = [
            Book.objects.create(
                title=f'Book {i}', 
                author=f'Author {i}', 
                genre='Test', 
                publication_year=2024,
                is_available=True
            ) for i in range(4)
        ]
        loan_url = reverse('loan-list')
        for book in books:
            loan_response = self.client.post(loan_url, {'book': book.id}, format='json')
        assert loan_response.status_code == status.HTTP_400_BAD_REQUEST
        assert Loan.objects.count() == 3

    def test_overdue_loans_tracking(self):
        book = Book.objects.create(
            title='Overdue Book', 
            author='Late Author', 
            genre='Drama', 
            publication_year=2024,
            is_available=True
        )
        overdue_loan = Loan.objects.create(
            book=book,
            reader=self.reader,
            return_date=timezone.now() - timezone.timedelta(days=1),
            returned=False
        )
        pending_url = reverse('loan-pending')
        response = self.client.get(pending_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['book'] == book.id
