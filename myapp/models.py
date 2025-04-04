from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
import pkg_resources

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.password = password 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True) 
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    role = models.CharField(max_length=20)
    password = models.CharField(max_length=100) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class DeliveryBoy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    
class ProductCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product_name} ({self.category.name})"
    
    
class SubCategory(models.Model):
    subcategory_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subcategory_name} ({self.product_category.product_name} - {self.category.name})"

class Product(models.Model):
    product_name = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)  # New field
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    quantity = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)  # Field for stock quantity
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    shelf_life = models.CharField(max_length=100, blank=True, null=True)  # Field for shelf life
    form_factor = models.CharField(max_length=100, blank=True, null=True)  # Field for form factor
    organic = models.BooleanField(default=False)  # Field for organic product
    common_name = models.CharField(max_length=100, blank=True, null=True)  # Field for common name
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_name.product_name} - {self.category.name} - {self.subcategory.subcategory_name if self.subcategory else 'No Subcategory'}"

    @property
    def farmer_address(self):
        return self.farmer.user.address


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} - {self.product}"
    
def total_price(self):
        return self.product.price * self.quantity
    
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Meta:
        unique_together = ('user', 'product')
                  
class Price_Chart(models.Model):
    product_name = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='price_chart_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.product_name.name} - {self.category.name} - {self.subcategory.name if self.subcategory else 'No Subcategory'} - {self.price} - {self.quantity}"
class OrderDetails(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderProduct')  # Many-to-many relationship with Product
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

    class Meta:
        verbose_name_plural = "Order Details"


# Intermediate model to store product-specific details within an order
class OrderProduct(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in order {self.order.id}"

class Payment(models.Model):
       user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
       order_details = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, null=True, blank=True)  # Allow null
       amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
       payment_id = models.CharField(max_length=100, unique=True)  # Payment ID from the payment gateway
       order_id = models.CharField(max_length=100, unique=True)    # Order ID from the payment gateway
       status = models.CharField(max_length=20)  # e.g., 'Success', 'Failed'
       created_at = models.DateTimeField(auto_now_add=True)
       def __str__(self):
           return f"Payment {self.payment_id} by {self.user.email}"
       
       def get_product_names(self):
        """Retrieve all product names associated with this payment."""
        order_details = self.orderdetails_set.all()  # Get all related OrderDetails
        return ", ".join([str(order_detail.product.product_name) for order_detail in order_details])
       
       @property
       def product_names(self):
        """Property to get product names for display in admin."""
        return self.get_product_names()
       
class FarmerPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_details = models.ForeignKey('OrderDetails', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)  # Automatically set the date to now when creating a record
    status = models.CharField(max_length=20)  # You can use choices for specific statuses if needed
    delivery_boy = models.ForeignKey('DeliveryBoy', null=True, blank=True, on_delete=models.SET_NULL)  # Optional delivery boy assignment

    def __str__(self):
        return f"Payment {self.id} by {self.user} on {self.date}"

class DeliveryAssignment(models.Model):
    delivery_boy = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'deliveryboy'})
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)  # Associate with Payment instead of Order
    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=[('Pending', 'Pending'), ('Delivered', 'Delivered')])

    def save(self, *args, **kwargs):
        # Check if the status is being changed to 'Delivered'
        if self.status == 'Delivered':
            # Update related Payment and OrderDetails status
            self.payment.status = 'Delivered'
            self.payment.order_details.order_status = 'Delivered'
            # Update payment status if needed
            self.payment.save()
            self.payment.order_details.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.delivery_boy.email} - Payment {self.payment.payment_id}"


class QualityResult(models.Model):
    image = models.ImageField(upload_to='quality_images/')
    status = models.CharField(max_length=20)
    reasons = models.TextField(null=True, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status
    

class Feedback(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating_value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class EdCat(models.Model):
    catid = models.AutoField(primary_key=True)
    catname = models.CharField(max_length=255)

    def __str__(self):
        return self.catname
    
class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    category = models.ForeignKey(EdCat, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='material_images/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    
class SeasonalCategory(models.Model):
    month_name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.month_name
    
    
    
class SeasonalProduct(models.Model):
    category = models.ForeignKey(SeasonalCategory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='seasonal_products/', blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} ({self.category.name})"
    
    
from django.db import models

class Event(models.Model):
    EVENT_MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='event_images/')  # Stores images in media/event_images
    description = models.TextField()
    registration_start_date = models.DateField()
    registration_end_date = models.DateField()
    event_date = models.DateField()
    mode = models.CharField(max_length=10, choices=EVENT_MODE_CHOICES)

    def __str__(self):
        return self.name
    
class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


class PlantDisease(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='disease_images/')
    description = models.TextField()
    tips_to_control = models.TextField()  # New field

    def __str__(self):
        return self.title
    
    
class Plant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    climate = models.CharField(max_length=255)
    soil_type = models.CharField(max_length=255)
    pesticide = models.CharField(max_length=255)
    pesticide_time = models.CharField(max_length=255)
    growth_duration = models.CharField(max_length=255)  # New field
    fertilizers_used = models.CharField(max_length=255)  # New field
    harvesting_season = models.CharField(max_length=255)  # New field

    def __str__(self):
        return self.name


from django.db import models

class PlantImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Prediction fields
    soil_type = models.CharField(max_length=50, blank=True)
    climate = models.CharField(max_length=50, blank=True)
    pesticide = models.CharField(max_length=100, blank=True)
    application_period = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Plant Image {self.id}"