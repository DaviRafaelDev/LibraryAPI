from django.db import models
from django.contrib.auth.models import User


def user_profile_picture_path(instance, filename):
    """Generate file path for user profile pictures."""
    return f'profile_pictures/user_{instance.user.id}/{filename}'


def book_cover_picture_path(instance, filename):
    """Generate file path for book cover images."""
    return f'book_covers/{instance.id}/{filename}'


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    publication_year = models.IntegerField()
    cover_image = models.ImageField(
        upload_to=book_cover_picture_path, 
        null=True, 
        blank=True, 
        verbose_name='Book Cover'
    )
    is_available = models.BooleanField(default=True)  # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def update_availability(self):
        """
        Update book availability based on active loans.
        """
        active_loans = self.loan_set.filter(returned=False).exists()
        self.is_available = not active_loans
        self.save()


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path, 
        null=True, 
        blank=True, 
        verbose_name='Profile Picture'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    loan_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    actual_return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.reader.user.username}"
