from django.db import models
from django.utils import timezone

# ------------------ STUDENT ------------------
class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    admission_number = models.CharField(max_length=20, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    student_class = models.CharField(max_length=20)
    stream = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)
    parent_name = models.CharField(max_length=50)
    parent_contact = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(upload_to="student_photos/", null=True, blank=True)

    class Meta:
        ordering = ["admission_number"]
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.full_name()} ({self.admission_number})"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ------------------ DISCIPLINE ------------------
class Discipline(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="discipline_records")
    date = models.DateField()
    offense = models.TextField()
    action_taken = models.TextField()
    teacher_in_charge = models.CharField(max_length=50)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Discipline Records"

    def __str__(self):
        return f"{self.student.full_name()} - {self.offense} on {self.date}"


# ------------------ STUDY BOOK ------------------
class StudyBook(models.Model):
    SUBJECT_CHOICES = [
        ("Mathematics", "Mathematics"),
        ("English", "English"),
        ("Kiswahili", "Kiswahili"),
        ("Biology", "Biology"),
        ("Chemistry", "Chemistry"),
        ("Physics", "Physics"),
        ("Geography", "Geography"),
        ("History", "History"),
        ("CRE", "CRE"),
        ("Business Studies", "Business Studies"),
        ("Agriculture", "Agriculture"),
        ("Computer Studies", "Computer Studies"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["subject", "title"]
        verbose_name_plural = "Study Books"

    def __str__(self):
        return f"{self.title} ({self.subject})"

    def borrowed_count(self):
        """Returns the number of copies currently borrowed."""
        return self.borrow_records.filter(returned=False).count()

    def available_copies(self):
        """Returns the number of available copies."""
        return max(self.total_copies - self.borrowed_count(), 0)

    def is_available(self):
        return self.available_copies() > 0


# ------------------ LIBRARY ------------------
class Library(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="library_records")
    book_title = models.CharField(max_length=100)  # Keep old field for backward compatibility
    book = models.ForeignKey(StudyBook, on_delete=models.SET_NULL, null=True, blank=True, related_name="borrow_records")
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="borrowed")

    class Meta:
        ordering = ["-borrow_date"]
        verbose_name_plural = "Library Records"

    def __str__(self):
        if self.book:
            return f"{self.book.title} ({self.status}) - {self.student.full_name()}"
        return f"{self.book_title} ({self.status}) - {self.student.full_name()}"


# ------------------ FEE ------------------
class Fee(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    term = models.CharField(max_length=10)
    amount_due = models.FloatField()
    amount_paid = models.FloatField()
    balance = models.FloatField(blank=True, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")

    class Meta:
        ordering = ["term"]
        verbose_name_plural = "Fees"

    def save(self, *args, **kwargs):
        self.balance = max(self.amount_due - self.amount_paid, 0)
        if self.balance == 0:
            self.payment_status = "paid"
        elif 0 < self.balance < self.amount_due:
            self.payment_status = "partial"
        else:
            self.payment_status = "unpaid"
        super(Fee, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name()} - {self.term} ({self.payment_status})"


# ------------------ PERFORMANCE ------------------
class Performance(models.Model):
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="performance_records")
    term = models.CharField(max_length=10)
    subject = models.CharField(max_length=50)
    marks = models.FloatField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, null=True, blank=True)
    teacher_comments = models.TextField(blank=True)

    class Meta:
        ordering = ["term", "subject"]
        verbose_name_plural = "Performance Records"

    def save(self, *args, **kwargs):
        if not self.grade:
            if self.marks >= 80:
                self.grade = "A"
            elif self.marks >= 70:
                self.grade = "B"
            elif self.marks >= 60:
                self.grade = "C"
            elif self.marks >= 50:
                self.grade = "D"
            elif self.marks >= 40:
                self.grade = "E"
            else:
                self.grade = "F"
        super(Performance, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name()} - {self.subject} ({self.term}): {self.marks} [{self.grade}]"
    
class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    term = models.CharField(max_length=20)
    amount_due = models.FloatField()
    amount_paid = models.FloatField()
    balance = models.FloatField()
    payment_status = models.CharField(max_length=20)
    date = models.DateTimeField(default=timezone.now)  # <-- new field

    def __str__(self):
        return f"{self.student} - {self.term}"
