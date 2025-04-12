# Enhanced E-Commerce Admin Interface Setup

This guide will help you set up the enhanced admin interface for your Django e-commerce application.

## 1. Install Required Packages

First, make sure you have installed all the required packages:

```bash
# Stop any running containers
make down

# Rebuild with new dependencies
docker-compose build

# Start the containers
make up
```

## 2. Run Migrations

Apply the database migrations to create the necessary tables:

```bash
make migrate
```

## 3. Create Superuser

Create an admin user to access the admin interface:

```bash
make createsuperuser
```

## 4. Collect Static Files

Collect the static files for the admin interface:

```bash
docker-compose exec web python manage.py collectstatic --no-input
```

## 5. Directory Structure

Make sure the following directories exist in your project:

```
templates/
└── admin/
    ├── dashboard.html
    └── login.html
static/
└── img/
    └── logo.svg
```

## 6. Access the Admin Interface

Now you can access the enhanced admin interface at:

```
http://localhost:8000/admin/
```

## 7. Admin Interface Features

The enhanced admin interface includes the following features:

### Custom Dashboard with E-Commerce Metrics
- Sales summary (today, week, month)
- Order status breakdown
- Recent orders
- Popular products
- Low stock alerts
- Customer metrics
- Recent reviews

### Enhanced Product Management
- Image previews
- Import/export functionality
- Advanced filtering and searching
- Inventory status indicators
- Rating display

### Enhanced Order Management
- Order status tracking
- Payment status indicators
- Customer information
- Order item details

### Enhanced User Management
- Order history
- Customer spending metrics
- User type indicators

## 8. Customizing the Admin Theme

You can customize the admin theme by modifying the Jazzmin settings in `settings.py`. The following themes are available:

- Default
- Cerulean
- Cosmo
- Cyborg
- Darkly
- Flatly
- Journal
- Litera
- Lumen
- Lux
- Materia
- Minty
- Pulse
- Sandstone
- Simplex
- Sketchy
- Slate
- Solar
- Spacelab
- Superhero
- United
- Yeti

To change the theme, update the `JAZZMIN_SETTINGS["theme"]` value in `settings.py`.

## 9. Troubleshooting

If you encounter any issues:

1. Check the Django logs for errors:
   ```bash
   make logs
   ```

2. Make sure all static files are collected:
   ```bash
   docker-compose exec web python manage.py collectstatic --no-input
   ```

3. Check that the templates directory is correctly configured in settings.py
