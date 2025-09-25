from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Student, Performance, Discipline, Library, Fee, StudyBook
from .forms import StudentForm, DisciplineForm, LibraryForm, FeeForm, PerformanceForm
from django.utils import timezone

# ----------------- LOGIN -----------------
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid username or password."
    return render(request, "students/login.html", {"error": error})

# ----------------- LOGOUT -----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

# ----------------- HOME / MAIN MENU -----------------
@login_required
def home(request):
    admission_number = request.GET.get("admission_number")
    error = None
    if admission_number:
        try:
            Student.objects.get(pk=admission_number)
            return redirect(reverse("student_dashboard", args=[admission_number]))
        except Student.DoesNotExist:
            error = f"Student with admission number {admission_number} not found."
    return render(request, "students/home.html", {"error": error})

# ----------------- CORE VIEWS -----------------
@login_required
def student_list(request):
    classes = {}
    for student in Student.objects.all().order_by("student_class", "stream", "last_name"):
        classes.setdefault(student.student_class, {}).setdefault(student.stream, []).append(student)
    return render(request, "students/student_list.html", {"classes": classes})

@login_required
def book_list(request):
    student = None
    try:
        student = Student.objects.get(admission_number=request.user.username)
    except Student.DoesNotExist:
        student = None

    if request.method == "POST":
        # Borrow a book
        if "borrow-book" in request.POST and student:
            book_id = request.POST.get("borrow-book")
            book = get_object_or_404(StudyBook, id=book_id)
            borrowed_count = Library.objects.filter(book=book, returned=False).count()
            if borrowed_count < book.total_copies:
                Library.objects.create(
                    student=student,
                    book=book,
                    borrow_date=timezone.now(),
                    returned=False,
                    status="Borrowed"
                )
            return redirect("book_list")

        # Return a book
        elif "return-book" in request.POST and student:
            book_id = request.POST.get("return-book")
            lib_record = Library.objects.filter(book_id=book_id, student=student, returned=False).last()
            if lib_record:
                lib_record.return_date = timezone.now()
                lib_record.returned = True
                lib_record.status = "Returned"
                lib_record.save()
            return redirect("book_list")

        # Delete a book
        elif "delete-book" in request.POST:
            book_id = request.POST.get("delete-book")
            book = get_object_or_404(StudyBook, id=book_id)
            book.delete()
            return redirect("book_list")

    subjects = {}
    for book in StudyBook.objects.all().order_by("subject", "title"):
        subject_name = dict(StudyBook.SUBJECT_CHOICES).get(book.subject, book.subject)
        borrowed_count = Library.objects.filter(book=book, returned=False).count()
        last_record = Library.objects.filter(book=book).order_by('-borrow_date').first()
        subjects.setdefault(subject_name, []).append({
            "book": book,
            "total_copies": book.total_copies,
            "borrowed": borrowed_count,
            "available": book.total_copies - borrowed_count,
            "last_record": last_record,
        })

    return render(request, "students/book_list.html", {
        "subjects": subjects,
        "student": student
    })

# ----------------- UPDATED LIBRARY PAGE -----------------
@login_required
def library_page(request):
    """Library page with search by student admission number and book title."""
    search_admission_number = request.GET.get("admission_number", "")
    search_title = request.GET.get("title", "")

    records = Library.objects.all().order_by("-borrow_date")

    if search_admission_number:
        records = records.filter(student__admission_number__icontains=search_admission_number)
    if search_title:
        records = records.filter(book__title__icontains=search_title)

    # Compute borrowed count per book
    book_borrowed_counts = {}
    for book_id in records.values_list("book_id", flat=True).distinct():
        borrowed_count = Library.objects.filter(book_id=book_id, returned=False).count()
        book_borrowed_counts[book_id] = borrowed_count

    return render(request, "students/library.html", {
        "records": records,
        "book_borrowed_counts": book_borrowed_counts,
        "search_admission_number": search_admission_number,
        "search_title": search_title,
    })

# ----------------- UPDATED LIBRARY ADD -----------------
@login_required
def library_add(request):
    """Add a new library borrow record respecting available copies."""
    if request.method == "POST":
        form = LibraryForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data["book"]
            borrowed_count = Library.objects.filter(book=book, returned=False).count()
            if borrowed_count < book.total_copies:
                library_record = form.save(commit=False)
                library_record.status = "Borrowed"
                library_record.returned = False
                library_record.borrow_date = timezone.now()
                library_record.save()
                return redirect("library_page")
            else:
                form.add_error("book", "No available copies to borrow.")
    else:
        form = LibraryForm()
    return render(request, "students/library_add.html", {"form": form})

# ----------------- OTHER VIEWS REMAIN UNCHANGED -----------------
@login_required
def student_profile(request, admission_number):
    student = get_object_or_404(Student, pk=admission_number)
    borrowed_books = student.borrowed_books.filter(returned=False)
    return render(request, "students/student_profile.html", {
        "student": student,
        "borrowed_books": borrowed_books,
    })

@login_required
def student_dashboard(request, admission_number):
    student = get_object_or_404(Student, pk=admission_number)
    discipline = student.discipline_records.all()
    library = student.library_records.all()
    fees = student.fees.all()
    performance = student.performance_records.all()

    avg_marks_data = performance.aggregate(avg=Avg("marks"))
    avg_marks = avg_marks_data["avg"] if avg_marks_data["avg"] else 0

    students_perf = Performance.objects.values(
        "student__admission_number", "student__first_name", "student__last_name", "student__stream"
    ).annotate(avg_marks=Avg("marks"))

    overall_sorted = sorted(students_perf, key=lambda x: -x["avg_marks"])
    overall_rank = next((idx + 1 for idx, s in enumerate(overall_sorted) if s["student__admission_number"] == admission_number), None)

    stream_perf = [s for s in students_perf if s["student__stream"] == student.stream]
    stream_perf.sort(key=lambda x: -x["avg_marks"])
    stream_rank = next((idx + 1 for idx, s in enumerate(stream_perf) if s["student__admission_number"] == admission_number), None)

    student_trend_qs = performance.values("term").annotate(avg_marks=Avg("marks")).order_by("term")
    student_trend_labels = [data["term"] for data in student_trend_qs]
    student_trend_values = [data["avg_marks"] for data in student_trend_qs]

    stream_perf_qs = Performance.objects.filter(student__stream=student.stream).values("term").annotate(avg_marks=Avg("marks")).order_by("term")
    stream_trend_labels = [data["term"] for data in stream_perf_qs]
    stream_trend_values = [data["avg_marks"] for data in stream_perf_qs]

    context = {
        "student": student,
        "discipline": discipline,
        "library": library,
        "fees": fees,
        "performance": performance,
        "avg_marks": avg_marks,
        "stream_rank": stream_rank,
        "overall_rank": overall_rank,
        "student_trend_labels": student_trend_labels,
        "student_trend_values": student_trend_values,
        "stream_trend_labels": stream_trend_labels,
        "stream_trend_values": stream_trend_values,
    }
    return render(request, "students/dashboard.html", context)

@login_required
def student_rankings(request, stream=None):
    students_perf = Performance.objects.values(
        "student__admission_number", "student__first_name", "student__last_name", "student__stream"
    ).annotate(avg_marks=Avg("marks"))

    class_ranked = []
    if stream:
        stream_perf = [s for s in students_perf if s["student__stream"] == stream]
        stream_perf.sort(key=lambda x: -x["avg_marks"])
        for idx, s in enumerate(stream_perf, start=1):
            class_ranked.append({
                "rank": idx,
                "admission_number": s["student__admission_number"],
                "name": f"{s['student__first_name']} {s['student__last_name']}",
                "avg_marks": s["avg_marks"],
            })

    overall_ranked_list = []
    for idx, s in enumerate(sorted(students_perf, key=lambda x: -x["avg_marks"]), start=1):
        overall_ranked_list.append({
            "rank": idx,
            "admission_number": s["student__admission_number"],
            "name": f"{s['student__first_name']} {s['student__last_name']}",
            "avg_marks": s["avg_marks"],
            "stream": s["student__stream"],
        })

    streams_perf = {}
    for s in students_perf:
        streams_perf.setdefault(s["student__stream"], []).append(s["avg_marks"])
    stream_avg_list = [{"stream": k, "avg_marks": sum(v)/len(v) if v else 0} for k, v in streams_perf.items()]
    stream_avg_list.sort(key=lambda x: -x["avg_marks"])

    context = {
        "stream": stream,
        "class_ranked": class_ranked,
        "overall_ranked": overall_ranked_list,
        "stream_avg_list": stream_avg_list,
    }
    return render(request, "students/rankings.html", context)

@login_required
def overall_entry_dashboard(request):
    student = None
    if request.method == "POST" and "search-admission" in request.POST:
        adm_no = request.POST.get("admission_number")
        try:
            student = Student.objects.get(admission_number=adm_no)
        except Student.DoesNotExist:
            student = None

    student_form = StudentForm(prefix="student", instance=student)
    discipline_form = DisciplineForm(prefix="discipline", initial={"student": student} if student else None)
    library_form = LibraryForm(prefix="library", initial={"student": student} if student else None)
    fee_form = FeeForm(prefix="fee", initial={"student": student} if student else None)
    performance_form = PerformanceForm(prefix="performance", initial={"student": student} if student else None)

    if request.method == "POST":
        if "student-submit" in request.POST:
            student_form = StudentForm(request.POST, request.FILES, prefix="student", instance=student)
            if student_form.is_valid():
                student_form.save()
                return redirect("overall_entry_dashboard")
        elif "discipline-submit" in request.POST:
            discipline_form = DisciplineForm(request.POST, prefix="discipline")
            if discipline_form.is_valid():
                discipline_form.save()
                return redirect("overall_entry_dashboard")
        elif "library-submit" in request.POST:
            library_form = LibraryForm(request.POST, prefix="library")
            if library_form.is_valid():
                library_form.save()
                return redirect("overall_entry_dashboard")
        elif "fee-submit" in request.POST:
            fee_form = FeeForm(request.POST, prefix="fee")
            if fee_form.is_valid():
                fee = fee_form.save(commit=False)
                fee.balance = fee.amount_due - fee.amount_paid
                fee.payment_status = "Paid" if fee.balance == 0 else "Partial" if fee.balance < fee.amount_due else "Unpaid"
                fee.save()
                return redirect("overall_entry_dashboard")
        elif "performance-submit" in request.POST:
            performance_form = PerformanceForm(request.POST, prefix="performance")
            if performance_form.is_valid():
                performance_form.save()
                return redirect("overall_entry_dashboard")

    context = {
        "student": student,
        "student_form": student_form,
        "discipline_form": discipline_form,
        "library_form": library_form,
        "fee_form": fee_form,
        "performance_form": performance_form,
    }
    return render(request, "students/overall_entry.html", context)

# ----------------- EXTRA PAGES -----------------
@login_required
def discipline_page(request):
    records = Discipline.objects.all().order_by("-date")
    return render(request, "students/discipline.html", {"records": records})

@login_required
def fees_page(request):
    records = Fee.objects.all().order_by("-date")
    return render(request, "students/fees.html", {"records": records})
