from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.html import format_html
from apps.orders.models import Order, Payment
from apps.products.models import Product, ProductReview
from apps.users.models import User


def get_date_range_filters():
    today = timezone.now().date()

    # Today
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    # This week (starting from Monday)
    week_start = today - timedelta(days=today.weekday())
    week_start = timezone.make_aware(timezone.datetime.combine(week_start, timezone.datetime.min.time()))
    week_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    # This month
    month_start = today.replace(day=1)
    month_start = timezone.make_aware(timezone.datetime.combine(month_start, timezone.datetime.min.time()))
    month_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    return {
        'today': {'start': today_start, 'end': today_end},
        'week': {'start': week_start, 'end': week_end},
        'month': {'start': month_start, 'end': month_end},
    }


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with key e-commerce metrics"""
    date_ranges = get_date_range_filters()

    # Sales metrics
    sales_metrics = {
        'today': Order.objects.filter(
            created_at__range=[date_ranges['today']['start'], date_ranges['today']['end']]).aggregate(
            count=Count('id'),
            total=Sum('total'),
        ),
        'week': Order.objects.filter(
            created_at__range=[date_ranges['week']['start'], date_ranges['week']['end']]).aggregate(
            count=Count('id'),
            total=Sum('total'),
        ),
        'month': Order.objects.filter(
            created_at__range=[date_ranges['month']['start'], date_ranges['month']['end']]).aggregate(
            count=Count('id'),
            total=Sum('total'),
        ),
        'all_time': Order.objects.aggregate(
            count=Count('id'),
            total=Sum('total'),
        ),
    }

    # Order status breakdown
    order_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    # Popular products
    popular_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]

    # Low stock products
    low_stock_products = Product.objects.filter(
        inventory__lt=10,
        is_available=True
    ).order_by('inventory')[:5]

    # Customer metrics
    customer_metrics = {
        'total': User.objects.count(),
        'new_today': User.objects.filter(
            date_joined__range=[date_ranges['today']['start'], date_ranges['today']['end']]).count(),
        'new_week': User.objects.filter(
            date_joined__range=[date_ranges['week']['start'], date_ranges['week']['end']]).count(),
        'new_month': User.objects.filter(
            date_joined__range=[date_ranges['month']['start'], date_ranges['month']['end']]).count(),
    }

    # Recent reviews
    recent_reviews = ProductReview.objects.select_related('product', 'user').order_by('-created_at')[:5]

    context = {
        'title': 'E-Commerce Dashboard',
        'sales_metrics': sales_metrics,
        'order_status': order_status,
        'recent_orders': recent_orders,
        'popular_products': popular_products,
        'low_stock_products': low_stock_products,
        'customer_metrics': customer_metrics,
        'recent_reviews': recent_reviews,
        # Links for viewing more
        'order_list_url': reverse('admin:orders_order_changelist'),
        'product_list_url': reverse('admin:products_product_changelist'),
        'customer_list_url': reverse('admin:users_user_changelist'),
        'review_list_url': reverse('admin:products_productreview_changelist'),
    }

    return render(request, 'admin/dashboard.html', context)