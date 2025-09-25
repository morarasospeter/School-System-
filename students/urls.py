from django.urls import path
from . import views

urlpatterns = [
    # ----------------- DEFAULT ROOT -----------------
    path('', views.login_view, name='root_login'),

    # ----------------- AUTH -----------------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ----------------- HOME / MAIN MENU -----------------
    path('home/', views.home, name='home'),
    path('menu/', views.home, name='menu'),  # Alias for template use

    # ----------------- STUDENT DASHBOARD -----------------
    path('dashboard/<str:admission_number>/', views.student_dashboard, name='student_dashboard'),
    path('profile/<str:admission_number>/', views.student_profile, name='student_profile'),

    # ----------------- STUDENT RANKINGS -----------------
    path('rankings/', views.student_rankings, name='rankings_overall'),
    path('rankings/<str:stream>/', views.student_rankings, name='rankings_stream'),

    # ----------------- OVERALL DATA ENTRY -----------------
    path('entry/', views.overall_entry_dashboard, name='overall_entry_dashboard'),

    # ----------------- EXTRA PAGES -----------------
    path('discipline/', views.discipline_page, name='discipline_page'),
    path('library/', views.library_page, name='library_page'),
    path('library/add/', views.library_add, name='library_add'),  # <- NEW: Add Book
    path('fees/', views.fees_page, name='fees_page'),

    # ----------------- CORE VIEWS -----------------
    path('students/', views.student_list, name='student_list'),
    path('books/', views.book_list, name='book_list'),
]
