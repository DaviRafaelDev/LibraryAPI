from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Book, Reader, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_year', 'is_available', 'created_at', 'updated_at')
    list_filter = ('genre', 'publication_year', 'is_available')
    search_fields = ('title', 'author')
    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'phone', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'user')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'reader_username', 'loan_date', 'return_date', 'returned', 'actual_return_date')
    list_filter = ('returned', 'loan_date', 'return_date')
    search_fields = ('book__title', 'reader__user__username')

    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book'

    def reader_username(self, obj):
        return obj.reader.user.username
    reader_username.short_description = 'Reader'


class ReaderInline(admin.StackedInline):
    model = Reader
    can_delete = False
    verbose_name_plural = 'Reader Profile'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ReaderInline,)
    list_display = BaseUserAdmin.list_display + ('has_reader_profile',)

    def has_reader_profile(self, user):
        return hasattr(user, 'reader')
    has_reader_profile.boolean = True
    has_reader_profile.short_description = 'Reader Profile'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)