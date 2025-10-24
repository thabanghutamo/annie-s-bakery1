# Annie's Bakery - Admin User Guide

## Overview

Welcome to the Annie's Bakery Admin Dashboard! This guide will help you manage your bakery's online presence, including products, orders, blog posts, and settings.

## Getting Started

### Logging In

1. Navigate to your bakery's website
2. Click "Login" in the top navigation
3. Enter your admin email and password
4. You'll be redirected to the admin dashboard

### Dashboard Overview

The admin dashboard provides a quick overview of your bakery's performance:

- **Product Count**: Total number of products in your catalog
- **Post Count**: Number of blog posts published
- **Order Count**: Total orders received
- **Custom Order Count**: Special/custom orders
- **Recent Orders**: Latest 5 orders with status
- **Recent Posts**: Latest 5 blog posts

## Product Management

### Viewing Products

1. From the dashboard, click "Products" in the navigation menu
2. View all products in a table format with:
   - Product title
   - Category
   - Price
   - Visibility status
   - Featured status
   - Actions (Edit/Delete)

### Adding New Products

1. Click "New Product" button or navigate to `/admin/products/new`
2. Fill in the product details:
   - **Title**: Product name (required)
   - **Description**: Detailed product description (required)
   - **Short Description**: Brief summary for listings
   - **Price**: Product price in South African Rand (required)
   - **Category**: Product category (required)
   - **Main Image**: Primary product image (optional)
   - **Additional Images**: Multiple supplementary images (optional)
   - **Visibility**: Show/hide product on store
   - **Featured**: Display on homepage
   - **Publish At**: Schedule publication date (optional)

3. Upload images by clicking "Choose File" buttons
4. Click "Save Product" to create the product

### Editing Products

1. From the products list, click the "Edit" button for any product
2. Modify any product details as needed
3. Upload new images to replace existing ones
4. Remove additional images by clicking the X button on existing images
5. Click "Save Product" to update

### Deleting Products

1. From the products list, click the "Delete" button for the product you want to remove
2. Confirm the deletion when prompted
3. The product will be permanently removed from your catalog

## Blog Management

### Viewing Blog Posts

1. Click "Blog" in the navigation menu
2. View all blog posts with:
   - Post title
   - Short description
   - Publication status
   - Creation date
   - Actions (Edit/Delete)

### Creating New Blog Posts

1. Click "New Post" or navigate to `/admin/blog/new`
2. Fill in the post details:
   - **Title**: Post headline (required)
   - **Short Description**: Brief summary (required)
   - **Content**: Full post content (required)
   - **Cover Image**: Main post image (optional)
   - **Additional Images**: Supplementary images (optional)
   - **Published**: Make post live immediately
   - **Publish At**: Schedule publication (optional)

3. Use the rich text editor for content formatting
4. Upload images as needed
5. Click "Save Post" to publish

### Editing Blog Posts

1. From the blog list, click "Edit" for any post
2. Modify content, images, and settings
3. Update publication status and date
4. Save changes

### Deleting Blog Posts

1. Click "Delete" next to any blog post
2. Confirm deletion when prompted

## Order Management

### Viewing Orders

1. Click "Orders" in the navigation menu
2. View all orders with filtering options:
   - **Status**: pending, confirmed, in_progress, ready, completed, cancelled
   - **Payment Status**: pending, paid, refunded, cancelled
   - **Search**: Filter by customer name, email, or order ID
   - **Type**: Standard orders or custom orders

### Managing Individual Orders

1. Click on any order ID to view details
2. View complete order information:
   - Customer details (name, email, phone)
   - Order items with quantities and prices
   - Total amount
   - Current status and payment status
   - Order notes and creation date

3. Update order status and payment status
4. Add internal notes for order tracking
5. Changes are automatically saved

### Batch Order Updates

1. On the orders page, select multiple orders using checkboxes
2. Choose "Batch Update" action
3. Set new status and/or payment status for all selected orders
4. Click "Update Orders" to apply changes

### Exporting Orders

1. Apply desired filters to orders list
2. Click "Export CSV" to download order data
3. Choose format: Standard Orders, Custom Orders, or All Orders
4. File will download automatically

## Settings Management

### Payment Gateway Configuration

1. Click "Settings" in the navigation menu
2. Configure payment settings:
   - **Payment Gateway**: Select payment provider (Stripe, Paystack, etc.)
   - **API Key**: Your payment provider's API key
   - **API Secret**: Your payment provider's secret key
   - **Webhook URL**: URL for payment notifications

3. Click "Save Settings" to update configuration

## User Interface Features

### Responsive Design

The admin interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

### Navigation

- **Desktop**: Full navigation menu in header
- **Mobile**: Collapsible menu accessible via hamburger icon

### Search and Filtering

- Order search by customer name, email, or order ID
- Order filtering by status and payment status
- Real-time search results

### Image Management

- Drag and drop image uploads
- Image preview before saving
- Multiple image support for products and blog posts
- Automatic image optimization

## Security Features

### Authentication

- Secure login with password hashing
- Session management
- Automatic logout on inactivity

### CSRF Protection

- All forms include CSRF tokens for security
- Automatic token validation

### Access Control

- Admin-only access to dashboard features
- Role-based permissions

## Troubleshooting

### Common Issues

**Can't upload images?**
- Check file size limits (typically 5MB max)
- Ensure image format is supported (JPG, PNG, GIF, WebP)
- Verify upload directory permissions

**Form not saving?**
- Check all required fields are filled
- Verify CSRF token is present
- Check for validation errors

**Orders not updating?**
- Ensure you have proper permissions
- Check network connection
- Try refreshing the page

### Getting Help

If you encounter issues not covered here:
1. Check the application logs
2. Contact technical support
3. Review the developer documentation

## Best Practices

### Product Management
- Use high-quality, well-lit product photos
- Write detailed, engaging descriptions
- Keep pricing current and competitive
- Regularly review and update product catalog

### Order Processing
- Respond to orders within 24 hours
- Update order status regularly
- Keep detailed notes for complex orders
- Maintain clear communication with customers

### Content Management
- Publish blog posts regularly to engage customers
- Use SEO-friendly titles and descriptions
- Include relevant keywords naturally
- Share posts on social media

### Security
- Use strong, unique passwords
- Log out when not using the admin panel
- Keep software and dependencies updated
- Monitor for unusual activity

---

*Last updated: October 24, 2025*