from django import forms
from .models import Student, Discipline, Library, Fee, Performance, StudyBook

# ------------------ STUDENT FORM ------------------
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'admission_number', 'first_name', 'last_name', 'dob', 'gender',
            'student_class', 'stream', 'contact_number', 'parent_name',
            'parent_contact', 'address', 'photo'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


# ------------------ DISCIPLINE FORM ------------------
class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ['student', 'date', 'offense', 'action_taken', 'teacher_in_charge']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'offense': forms.Textarea(attrs={'rows': 2}),
            'action_taken': forms.Textarea(attrs={'rows': 2}),
        }


# ------------------ LIBRARY FORM ------------------
class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ['student', 'book', 'book_title', 'borrow_date', 'return_date', 'status', 'returned']
        widgets = {
            'borrow_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        returned = cleaned_data.get('returned')

        # Ensure book has available copies if borrowing
        if book and not returned:
            if book.available_copies() <= 0:
                self.add_error('book', f"No available copies of '{book.title}' to borrow.")


# ------------------ FEE FORM ------------------
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'term', 'amount_due', 'amount_paid']
        # balance and payment_status are calculated automatically

    def clean(self):
        cleaned_data = super().clean()
        amount_due = cleaned_data.get("amount_due")
        amount_paid = cleaned_data.get("amount_paid")

        if amount_due is not None and amount_paid is not None:
            if amount_paid > amount_due:
                self.add_error('amount_paid', "Amount paid cannot be more than amount due.")


# ------------------ PERFORMANCE FORM ------------------
class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ['student', 'term', 'subject', 'marks', 'teacher_comments']
        widgets = {
            'teacher_comments': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        if marks < 0 or marks > 100:
            raise forms.ValidationError("Marks must be between 0 and 100.")
        return marks


# ------------------ STUDY BOOK FORM ------------------
class StudyBookForm(forms.ModelForm):
    class Meta:
        model = StudyBook
        fields = ['title', 'author', 'subject', 'isbn', 'total_copies']

    def clean_total_copies(self):
        total = self.cleaned_data.get('total_copies')
        if total < 1:
            raise forms.ValidationError("Total copies must be at least 1.")
        return total
