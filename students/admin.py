from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Discipline, Library, Fee, Performance


# ------------------ INLINE ADMINS ------------------
class DisciplineInline(admin.TabularInline):
    model = Discipline
    extra = 1
    fields = ("date", "offense", "action_taken", "teacher_in_charge")
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "📌 Discipline Record"
    verbose_name_plural = "📌 Discipline Records"


class LibraryInline(admin.TabularInline):
    model = Library
    extra = 1
    fields = ("book_title", "borrow_date", "return_date", "status")
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "📚 Library Record"
    verbose_name_plural = "📚 Library Records"


class FeeInline(admin.TabularInline):
    model = Fee
    extra = 1
    fields = ("term", "amount_due", "amount_paid", "balance", "payment_status")
    readonly_fields = ("balance", "payment_status")
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "💰 Fee Record"
    verbose_name_plural = "💰 Fee Records"


class PerformanceInline(admin.TabularInline):
    model = Performance
    extra = 1
    fields = ("term", "subject", "marks", "grade", "teacher_comments")
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "📊 Performance Record"
    verbose_name_plural = "📊 Performance Records"


# ------------------ STUDENT ADMIN ------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("admission_number", "full_name", "student_class", "stream", "show_photo")
    search_fields = ("admission_number", "first_name", "last_name", "stream", "student_class")
    list_filter = ("gender", "student_class", "stream")

    # Attach inlines (collapsible + renamed)
    inlines = [DisciplineInline, LibraryInline, FeeInline, PerformanceInline]

    # Show photo in list view
    def show_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.photo.url)
        return "No Photo"
    show_photo.short_description = "Photo"

    # Combine first and last name
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Full Name"

    # Custom fieldsets to organize detail view
    fieldsets = (
        ("Student Information", {
            "fields": ("admission_number", "first_name", "last_name", "dob", "gender", "student_class", "stream")
        }),
        ("Contact Information", {
            "fields": ("contact_number", "parent_name", "parent_contact", "address")
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview")
        }),
    )

    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="150" height="150" style="border-radius:10px;" />', obj.photo.url)
        return "No Photo Uploaded"
    photo_preview.short_description = "Photo Preview"


# ------------------ DISCIPLINE ADMIN ------------------
@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "offense", "action_taken", "teacher_in_charge")
    search_fields = ("student__admission_number", "student__first_name", "student__last_name", "offense")
    list_filter = ("date", "teacher_in_charge")


# ------------------ LIBRARY ADMIN ------------------
@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("student", "book_title", "borrow_date", "return_date", "status")
    search_fields = ("student__admission_number", "student__first_name", "student__last_name", "book_title")
    list_filter = ("status", "borrow_date")


# ------------------ FEE ADMIN ------------------
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ("student", "term", "amount_due", "amount_paid", "balance", "payment_status")
    search_fields = ("student__admission_number", "student__first_name", "student__last_name", "term")
    list_filter = ("payment_status", "term")


# ------------------ PERFORMANCE ADMIN ------------------
@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("student", "term", "subject", "marks", "grade")
    search_fields = ("student__admission_number", "student__first_name", "student__last_name", "subject")
    list_filter = ("term", "grade")
