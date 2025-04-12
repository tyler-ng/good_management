from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import path


class ECommerceAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = _('E-Commerce Admin')

    # Text to put in each page's <h1> (and above login form).
    site_header = _('E-Commerce Administration')

    # Text to put at the top of the admin index page.
    index_title = _('Dashboard')

    # URL for the "View site" link at the top of each admin page.
    site_url = '/'

    def get_urls(self):
        from core.dashboard import admin_dashboard

        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', admin_dashboard, name='admin_dashboard'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        # Redirect the admin index to our custom dashboard
        from django.shortcuts import redirect
        return redirect('admin:admin_dashboard')


# Register the custom admin site
admin_site = ECommerceAdminSite(name='ecommerce_admin')