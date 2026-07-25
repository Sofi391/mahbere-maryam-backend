from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'members',      views.MemberViewSet,      basename='member')
router.register(r'meetings',     views.MeetingViewSet,     basename='meeting')
router.register(r'attendance',   views.AttendanceViewSet,  basename='attendance')
router.register(r'contributions',views.ContributionViewSet,basename='contribution')
router.register(r'penalties',    views.PenaltyViewSet,     basename='penalty')
router.register(r'penalty-rules',views.PenaltyRuleViewSet, basename='penalty-rule')
router.register(r'expenses',     views.ExpenseViewSet,     basename='expense')
router.register(r'announcements',views.AnnouncementViewSet,basename='announcement')
router.register(r'manual-payments', views.ManualPaymentViewSet, basename='manual-payment')

urlpatterns = [
    path('', include(router.urls)),

    # Reports (admin only)
    path('reports/monthly/<int:meeting_id>/', views.MonthlyReportView.as_view(), name='monthly-report'),
    path('reports/yearly/<int:ethiopian_year>/', views.YearlyReportView.as_view(), name='yearly-report'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
