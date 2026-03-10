from django.urls import path

from .views import WorkerDashboardView, WorkerLoginView, WorkerLogoutView


urlpatterns = [
	path("", WorkerLoginView.as_view(), name="login"),
	path("accounts/login/", WorkerLoginView.as_view(), name="accounts_login"),
	path("dashboard/", WorkerDashboardView.as_view(), name="worker_dashboard"),
	path("logout/", WorkerLogoutView.as_view(), name="logout"),
]
