
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Farmer, Customer, DeliveryBoy
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate, login
from .models import Category,Product,ProductCategory
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .models import Product, Cart, SubCategory
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth import logout
from decimal import Decimal, InvalidOperation
from .models import Product, Wishlist, Price_Chart,Price_Chart
from django.http import HttpResponseBadRequest
from django.db.models import Sum,Q
import re
from django.http import HttpResponse
from django.core.paginator import Paginator
import razorpay
from .models import Product
import pkg_resources
from .models import Cart, Payment, DeliveryAssignment, OrderDetails,FarmerPayment



def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        pincode = request.POST['pincode']
        role = request.POST['role']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if not User.objects.filter(email=email).exists():
                otp = get_random_string(length=6, allowed_chars='0123456789')
                request.session['otp'] = otp
                request.session['user_data'] = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'pincode': pincode,
                    'role': role,
                    'password': password
                }
                
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                return redirect('verify_otp')
            else:
                return render(request, 'register.html', {'error': 'Email already exists'})
        else:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
    return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        if otp == request.session.get('otp'):
            user_data = request.session.get('user_data')
            user = User.objects.create(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                address=user_data['address'],
                pincode=user_data['pincode'],
                password=user_data['password'],
                role=user_data['role']
            )
            if user_data['role'] == 'farmer':
                Farmer.objects.create(user=user)
            elif user_data['role'] == 'customer':
                Customer.objects.create(user=user)
            elif user_data['role'] == 'deliveryboy':
                DeliveryBoy.objects.create(user=user)
                
            del request.session['otp']
            del request.session['user_data']
            
            return redirect('login')
        else:
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})
    return render(request, 'verify_otp.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        if email == 'admin@gmail.com' and password == 'Admin@123':
            # Use Django's login function
            return redirect('admin_dashboard')

        try:
            user = User.objects.get(email=email, password=password)
            login(request, user)  # Use Django's login function
            
            if user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            elif user.role == 'deliveryboy':
                return redirect('deliveryboy_dashboard')
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        messages.error(request, "You do not have permission to access this page.")
        # return redirect('login')  # or another appropriate page

    context = {
        'name': request.user.name,
        'user_id': request.user.id
    }
    return render(request, 'customer_dashboard.html', context)


@login_required
def farmer_dashboard(request):
    if request.user.role != 'farmer':
        messages.error(request, "You do not have permission to access this page.")
        # return redirect('login')  # or another appropriate page

    context = {
        'farmer_id': request.user.id,
    }
    return render(request, 'farmer_dashboard.html', context)



@login_required
def deliveryboy_dashboard(request):
    if request.user.role != 'deliveryboy':
        messages.error(request, "You do not have permission to access this page.")
        # return redirect('login')  # or another appropriate page

    context = {
        'farmer_id': request.user.id,
    }
    return render(request, 'deliveryboy_dashboard.html', context)



def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def check_email(request):
    email = request.POST.get('email')
    if User.objects.filter(email=email).exists():
        return JsonResponse({'is_unique': False})
    return JsonResponse({'is_unique': True})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/reset_password/{uid}/{token}/')

            message = render_to_string('reset_password_email.html', {
                'user': user,
                'reset_link': reset_link,
            })

            send_mail(
                'Password Reset Request',
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return render(request, 'forgot_password.html', {'message': 'A reset link has been sent to your email address.'})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Email does not exist'})
    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.password = password  # Store password in plain text
                    user.save()
                    return redirect('login')
                else:
                    return render(request, 'reset_password.html', {'error': 'Invalid token'})
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return render(request, 'reset_password.html', {'error': 'Invalid link'})
        else:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})
    return render(request, 'reset_password.html')



@login_required
def all_users_view(request):
    # Assuming you're using the logged-in user's data
    user = request.user
    context = {
        'customer': user
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == 'POST':
        # Extract data from POST request
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')

        # Update the user instance with new data
        user.name = name
        user.phone = phone
        user.address = address
        user.pincode = pincode

        # Save the changes to the database
        user.save()

        return redirect('profile')  # Redirect to profile page after saving

    return render(request, 'edit_profile.html', {'user': user})



@login_required
def farmer_profile_view(request):
    # Assuming you're using the logged-in user's data
    user = request.user
    context = {
        'farmer': user
    }
    return render(request, 'farmer_profile.html', context)

@login_required
def farmer_profile_edit_view(request):
    user = request.user

    if request.method == 'POST':
        # Update user fields based on POST data
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.pincode = request.POST.get('pincode')
        
        # Save changes to the database
        user.save()
        
        # Redirect to the profile view after successful update
        return redirect('farmer_profile')

    # Render profile edit page with current user data
    context = {
        'user': user
    }
    return render(request, 'farmer_profile_edit.html', context)


@login_required
def deliveryboy_profile_view(request):
    # Get the currently logged-in user's data
    user = request.user
    context = {
        'delivery_boy': user
    }
    return render(request, 'deliveryboy_profile.html', context)


@login_required
def deliveryboy_profile_edit_view(request):
    user = request.user

    if request.method == 'POST':
        # Update user fields based on POST data
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.pincode = request.POST.get('pincode')
        
        # Save changes to the database
        user.save()
        
        # Redirect to the delivery boy profile view after a successful update
        return redirect('deliveryboy_profile')

    # Render profile edit page with current user data
    context = {
        'delivery_boy': user
    }
    return render(request, 'deliveryboy_profile_edit.html', context)



def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {
        'users': users,
    })

def filter_users(request, role):
    users = User.objects.filter(role=role)
    return render(request, 'manage_users.html', {'users': users})

def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = 'active'
    user.is_active = True
    user.save()

    message = request.POST.get('message', '')
    
    # Send activation email
    send_mail(
        'Account Activated',
        f'Hello {user.name},\n\nYour account has been activated.\n\n{message}\n\nBest regards,\nGrocery store',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    
    messages.success(request, f'User {user.email} has been activated.')
    return redirect('manage_users')


def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = 'inactive'
    user.is_active = False
    user.save()

    message = request.POST.get('message', '')

    # Send deactivation email
    send_mail(
        'Account Deactivated',
        f'Hello {user.name},\n\nYour account has been deactivated.\n\n{message}\n\nBest regards,\nGrocery store',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

    messages.success(request, f'User {user.email} has been deactivated.')
    return redirect('manage_users')

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_users')


def list_categories(request):
    categories = Category.objects.all()
    return render(request, 'list_categories.html', {'categories': categories})


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip().lower()  # Convert to lowercase and strip whitespace
        if not name:
            return render(request, 'add_category.html', {'error': 'Category name is required.'})
        
        # Check if category already exists (case-insensitive)
        if Category.objects.filter(name__iexact=name).exists():
            return render(request, 'add_category.html', {'error': 'Category already exists.'})

        # Create new category
        Category.objects.create(name=name)
        return render(request, 'add_category.html', {'message': 'Category added successfully.'})

    return render(request, 'add_category.html')

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        name_regex = re.compile(r'^[A-Za-z\s]+$')
        
        if not name:
            return render(request, 'edit_category.html', {'category': category, 'error': 'Category name is required.'})

        if not name_regex.match(name):
            return render(request, 'edit_category.html', {'category': category, 'error': 'Category name must contain only letters and spaces.'})

        # Check if a category with the same name exists (case-insensitive)
        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            return render(request, 'edit_category.html', {'category': category, 'error': 'Category already exists.'})

        category.name = name
        category.save()
        return redirect('list_categories')

    return render(request, 'edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('list_categories')
    
    
def add_product(request):
    if request.method == 'POST':
        product_name_id = request.POST['product_name']
        category_id = request.POST['category']
        subcategory_id = request.POST.get('subcategory')  # Get subcategory from POST data
        price = request.POST['price']
        description = request.POST['description']
        quantity = request.POST['quantity']
        stock = request.POST['stock']
        shelf_life = request.POST.get('shelf_life', '')  # New field
        form_factor = request.POST.get('form_factor', '')  # New field
        organic = 'organic' in request.POST  # Checkbox for boolean field
        common_name = request.POST.get('common_name', '')  # New field
        image = request.FILES.get('image')  # Use get to handle cases where image might not be provided
        
        farmer = get_object_or_404(Farmer, user=request.user)

        product_name = get_object_or_404(ProductCategory, id=product_name_id)
        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(SubCategory, id=subcategory_id) if subcategory_id else None

        # Check for duplicate product
        existing_product = Product.objects.filter(
            product_name=product_name,
            category=category,
            subcategory=subcategory
        ).exists()

        if existing_product:
            # Handle duplicate product case (e.g., show an error message)
            return render(request, 'add_product.html', {
                'categories': Category.objects.all(),
                'product_categories': ProductCategory.objects.all(),
                'subcategories': SubCategory.objects.filter(category=category),
                'error_message': 'Product with this name, category, and subcategory already exists.',
                'farmer': farmer  # Pass farmer to template to display address
            })

        # If no duplicate, create and save the new product
        product = Product(
            product_name=product_name,
            category=category,
            subcategory=subcategory,
            price=price,
            description=description,
            quantity=quantity,
            stock=stock,
            shelf_life=shelf_life,
            form_factor=form_factor,
            organic=organic,
            common_name=common_name,
            image=image,
            farmer=farmer
        )
        product.save()
        return redirect('list_products')

    categories = Category.objects.all()
    product_categories = ProductCategory.objects.all()
    subcategories = SubCategory.objects.none()  # Default to no subcategories
    farmer = get_object_or_404(Farmer, user=request.user)  # Fetch farmer information

    return render(request, 'add_product.html', {
        'categories': categories,
        'product_categories': product_categories,
        'subcategories': subcategories,
        'farmer': farmer  # Pass farmer to template to display address
    })

def list_products(request):
    products = Product.objects.all()
    return render(request, 'list_products.html', {'products': products})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name_id = request.POST.get('product_name')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        price = request.POST.get('price')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        stock = request.POST.get('stock')
        shelf_life = request.POST.get('shelf_life', '')  # New field
        form_factor = request.POST.get('form_factor', '')  # New field
        organic = 'organic' in request.POST  # Checkbox for boolean field
        common_name = request.POST.get('common_name', '')  # New field
        image = request.FILES.get('image')  # Use get to handle cases where image might not be provided

        # Handle potential None values for foreign key fields
        product_name = get_object_or_404(ProductCategory, id=product_name_id) if product_name_id else product.product_name
        category = get_object_or_404(Category, id=category_id) if category_id else product.category
        subcategory = get_object_or_404(SubCategory, id=subcategory_id) if subcategory_id else product.subcategory

        # Update the product fields
        product.product_name = product_name
        product.category = category
        product.subcategory_id = subcategory_id
        product.price = price
        product.description = description
        product.quantity = quantity
        product.stock = stock
        product.shelf_life = shelf_life
        product.form_factor = form_factor
        product.organic = organic
        product.common_name = common_name

        if image:
            # Save the new image file
            product.image = image

        product.save()
        return redirect('list_products')  # Adjust the redirect URL if necessary

    # Fetch categories, product categories, and subcategories for the form
    categories = Category.objects.all()
    product_categories = ProductCategory.objects.all()
    subcategories = SubCategory.objects.filter(category=product.category) if product.category else SubCategory.objects.none()

    return render(request, 'edit_product.html', {
        'product': product,
        'categories': categories,
        'product_categories': product_categories,
        'subcategories': subcategories
    })
    
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('list_products')


def list_category_products(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    return render(request, 'list_category_products.html', {
        'categories': categories,
        'products': products
    })


def list_category_products(request):
    # Fetch all categories and products
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Render the template with categories and products
    return render(request, 'list_category_products.html', {
        'categories': categories,
        'products': products
    })
    
    
    

def add_product_category(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        product_name = request.POST.get('product_name').strip()

        # Validation for empty fields
        if not category_id:
            return render(request, 'add_product_category.html', {'categories': categories, 'error': 'Category is required.'})
        if not product_name:
            return render(request, 'add_product_category.html', {'categories': categories, 'error': 'Product name is required.'})
        
        # Check if product name contains only alphabetic characters
        if not product_name.isalpha():
            return render(request, 'add_product_category.html', {'categories': categories, 'error': 'Product name must contain only alphabetic characters.'})

        # Check for existing product in the same category
        if ProductCategory.objects.filter(category_id=category_id, product_name__iexact=product_name).exists():
            return render(request, 'add_product_category.html', {'categories': categories, 'error': 'Product with this name already exists in the selected category.'})
        
        # Create new product category
        category = get_object_or_404(Category, id=category_id)
        ProductCategory.objects.create(category=category, product_name=product_name)
        return redirect('view_product_categories')

    return render(request, 'add_product_category.html', {'categories': categories})

# View to list all product categories
def view_product_categories(request):
    product_categories = ProductCategory.objects.all()
    
    # Set up pagination
    paginator = Paginator(product_categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'view_product_categories.html', {'page_obj': page_obj})


# View to edit a product category
def edit_product_category(request, id):
    product_category = get_object_or_404(ProductCategory, id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        product_name = request.POST.get('product_name').strip()

        # Validation for empty fields
        if not category_id:
            return render(request, 'edit_product_category.html', {'product_category': product_category, 'categories': categories, 'error': 'Category is required.'})
        if not product_name:
            return render(request, 'edit_product_category.html', {'product_category': product_category, 'categories': categories, 'error': 'Product name is required.'})
        
        # Check for existing product in the same category
        if ProductCategory.objects.filter(category_id=category_id, product_name__iexact=product_name).exclude(id=product_category.id).exists():
            return render(request, 'edit_product_category.html', {'product_category': product_category, 'categories': categories, 'error': 'Product with this name already exists in the selected category.'})
        
        # Update product category
        product_category.category_id = category_id
        product_category.product_name = product_name
        product_category.save()
        return redirect('view_product_categories')

    return render(request, 'edit_product_category.html', {'product_category': product_category, 'categories': categories})

# View to delete a product category
def delete_product_category(request, id):
    product_category = get_object_or_404(ProductCategory, id=id)
    product_category.delete()
    return redirect('view_product_categories')



def add_subcategory(request):
    categories = Category.objects.all()
    product_categories = ProductCategory.objects.all()

    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name').strip()
        category_id = request.POST.get('category')
        product_category_id = request.POST.get('product_category')

        # Validation for empty fields
        if not subcategory_name:
            return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories, 'error': 'Subcategory name is required.'})
        if not category_id:
            return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories, 'error': 'Category is required.'})
        if not product_category_id:
            return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories, 'error': 'Product Category is required.'})

        # Check if subcategory name contains only alphabetic characters
        if not subcategory_name.isalpha():
            return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories, 'error': 'Subcategory name must contain only alphabetic characters.'})

        # Check for existing subcategory in the same product category
        if SubCategory.objects.filter(product_category_id=product_category_id, subcategory_name__iexact=subcategory_name).exists():
            return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories, 'error': 'Subcategory with this name already exists in the selected product category.'})

        # Create new subcategory
        category = get_object_or_404(Category, id=category_id)
        product_category = get_object_or_404(ProductCategory, id=product_category_id)
        SubCategory.objects.create(subcategory_name=subcategory_name, category=category, product_category=product_category)

        return redirect('view_subcategories')

    return render(request, 'add_subcategory.html', {'categories': categories, 'product_categories': product_categories})

def view_subcategories(request):
    subcategories_list = SubCategory.objects.all()
    paginator = Paginator(subcategories_list, 10)  # Show 10 subcategories per page

    page_number = request.GET.get('page')
    subcategories = paginator.get_page(page_number)

    return render(request, 'view_subcategories.html', {'subcategories': subcategories})

def edit_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    
    if request.method == 'POST':
        subcategory.subcategory_name = request.POST.get('subcategory_name')
        category_id = request.POST.get('category')
        product_category_id = request.POST.get('product_category')
        
        subcategory.category = get_object_or_404(Category, id=category_id)
        subcategory.product_category = get_object_or_404(ProductCategory, id=product_category_id)
        
        subcategory.save()
        
        messages.success(request, 'Subcategory updated successfully!')
        return redirect('view_subcategories')
    
    categories = Category.objects.all()
    product_categories = ProductCategory.objects.all()
    return render(request, 'edit_subcategory.html', {
        'subcategory': subcategory,
        'categories': categories,
        'product_categories': product_categories
    })

def delete_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    subcategory.delete()
    messages.success(request, 'Subcategory deleted successfully!')
    return redirect('view_subcategories')
  
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if stock is sufficient
        if product.stock >= quantity:
            # Add to cart logic
            cart, created = Cart.objects.get_or_create(user=request.user)  # Assuming you have user in your session or passed as a parameter
            cart_item, created = cart.items.get_or_create(product=product)
            cart_item.quantity += quantity
            cart_item.save()

            # Reduce product stock
            product.stock -= quantity
            product.save()
            return redirect('cart_view')  # Redirect to a cart view page or wherever appropriate
        else:
            # Handle the case where stock is insufficient
            return render(request, 'product_detail.html', {'product': product, 'error': 'Not enough stock available.'})

    return render(request, 'product_detail.html', {'product': product})


def contact_view(request):
    return render(request, 'contact.html', {'user': request.user})



@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        user = request.user

        # Check if the product is already in the user's wishlist
        if not Wishlist.objects.filter(user=user, product=product).exists():
            Wishlist.objects.create(user=user, product=product)

        return redirect('wishlist_page')  # Redirect to the wishlist page or wherever you prefer

@login_required
def wishlist_page(request):
    # Fetch all wishlist items for the logged-in user
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def wishlist_view(request):
    # Your logic to handle the wishlist
    return render(request, 'wishlist.html')


@csrf_exempt
def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        wishlist_item = get_object_or_404(Wishlist, product_id=product_id, user=request.user)
        wishlist_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
    
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})


def admin_dashboard(request):
    # Fetch counts of farmers, customers, and delivery boys
    farmer_count = Farmer.objects.count()
    customer_count = Customer.objects.count()
    deliveryboy_count = DeliveryBoy.objects.count()

    # Fetch all products
    products = Product.objects.all()

    # Prepare context
    context = {
        'farmer_count': farmer_count,
        'customer_count': customer_count,
        'deliveryboy_count': deliveryboy_count,
        'products': products,
    }

    # Render the template with context
    return render(request, 'admin_dashboard.html', context)

def admin_product_view(request):
    products = Product.objects.select_related('farmer__user').all()
    return render(request, 'admin_product_view.html', {'products': products})

# views.py
from django.shortcuts import render, redirect
from .models import Price_Chart, Category, ProductCategory, SubCategory

def add_price_chart(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory', None)
        price = request.POST.get('price')
        date = request.POST.get('date')
        quantity = request.POST.get('quantity')
        image = request.FILES.get('image')
        
        # Create a new Price_Chart entry
        Price_Chart.objects.create(
            product_name_id=product_name,
            category_id=category,
            subcategory_id=subcategory,
            price=price,
            date=date,
            quantity=quantity,
            image=image
        )
        return redirect('view_price_charts')
    else:
        categories = Category.objects.all()
        products = ProductCategory.objects.all()
        subcategories = SubCategory.objects.all()
        context = {
            'categories': categories,
            'products': products,
            'subcategories': subcategories,
        }
        return render(request, 'add_price_chart.html', context)


def view_price_charts(request):
    price_charts_list = Price_Chart.objects.all()
    paginator = Paginator(price_charts_list, 10)  # Show 10 price charts per page
    page_number = request.GET.get('page')
    price_charts = paginator.get_page(page_number)
    return render(request, 'view_price_charts.html', {'price_charts': price_charts})
    
def edit_price_chart(request, pk):
    price_chart = get_object_or_404(Price_Chart, pk=pk)
    if request.method == 'POST':
        product_id = request.POST.get('product_name')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        price = request.POST.get('price')
        date = request.POST.get('date')
        quantity = request.POST.get('quantity')
        image = request.FILES.get('image')

        # Update PriceChart instance
        price_chart.product_name = ProductCategory.objects.get(id=product_id)
        price_chart.category = Category.objects.get(id=category_id)
        price_chart.subcategory = SubCategory.objects.get(id=subcategory_id)
        price_chart.price = price
        price_chart.date = date
        price_chart.quantity = quantity

        # Handle image upload
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            price_chart.image = fs.url(filename)
        
        price_chart.save()
        messages.success(request, 'Price Chart updated successfully.')
        return redirect('view_price_charts')  # Redirect to the list of price charts
    else:
        categories = Category.objects.all()
        subcategories = SubCategory.objects.all()
        product_categories = ProductCategory.objects.all()
        context = {
            'price_chart': price_chart,
            'categories': categories,
            'subcategories': subcategories,
            'product_categories': product_categories
        }
        return render(request, 'edit_price_chart.html', context)
    
def delete_price_chart(request, pk):
    price_chart = get_object_or_404(Price_Chart, id=pk)
    price_chart.delete()
    return redirect('view_price_charts')


def price_chart_customer(request):
    # Query all price charts
    price_charts = Price_Chart.objects.all()
    
    # Pass price charts to the template
    return render(request, 'price_chart_customer.html', {'price_charts': price_charts})



def compare_product_prices(request):
    product_price_mismatches = []

    # Fetch all products
    products = Product.objects.all()

    for product in products:
        # Get corresponding price chart entries based on product name, category, and quantity
        price_chart_entries = Price_Chart.objects.filter(
            product_name=product.product_name,
            category=product.category,
            quantity=product.quantity
        )

        # Compare prices for each price chart entry
        for price_chart_entry in price_chart_entries:
            if product.price > price_chart_entry.price:
                farmer_email = product.farmer.user.email  # Assuming Farmer model has a OneToOne relationship with User model
                product_price_mismatches.append({
                    'product_name': product.product_name,
                    'category': product.category,
                    'product_price': product.price,
                    'price_chart_price': price_chart_entry.price,
                    'date': price_chart_entry.date,
                    'farmer_email': farmer_email
                })

    return render(request, 'compare_prices.html', {
        'product_price_mismatches': product_price_mismatches,
    })



# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = Decimal(request.POST.get('quantity', 1))  # Use Decimal for precision
    total_price = product.price * quantity  # Calculate the total price

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity, 'total_price': total_price}
    )

    if not created:  # If the cart item already exists, update the quantity and total price
        cart_item.quantity += quantity
        cart_item.total_price += total_price
        cart_item.save()

    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)  # Fetch the cart items for the logged-in user

    # Calculate the grand total by summing the total price of each cart item
    grand_total = sum(item.total_price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total,  # Pass the grand total to the template
    }
    return render(request, 'view_cart.html', context)

@login_required
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.delete()  # Remove the item from the cart
        return redirect('view_cart')  # Redirect back to the cart view

    return HttpResponseBadRequest("Invalid request method")

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        # Retrieve the cart item by ID
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        
        # Get the new quantity from the form data
        new_quantity = request.POST.get('quantity')
        
        # Convert the quantity to a Decimal for accuracy
        try:
            new_quantity = Decimal(new_quantity)
            if new_quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except (InvalidOperation, ValueError):
            # Handle invalid input
            return HttpResponseBadRequest("Invalid quantity provided.")
        
        # Ensure the new quantity does not exceed stock
        if new_quantity > cart_item.product.stock:
            return HttpResponseBadRequest("Requested quantity exceeds available stock.")
        
        # Update the cart item's quantity and total price
        cart_item.quantity = new_quantity
        cart_item.total_price = new_quantity * cart_item.product.price
        
        # Save the changes to the database
        cart_item.save()
        
        # Redirect the user back to the cart view
        return redirect('view_cart')

@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    grand_total = sum(item.product.price * item.quantity for item in cart_items)  # Calculate grand total

    # Check if the cart is empty
    if not cart_items.exists():
        return redirect('view_cart')  # Redirect if the cart is empty

    # Context data to pass to the template
    context = {
        'user': request.user,  # Current logged-in user
        'cart_items': cart_items,  # Cart items
        'grand_total': grand_total,  # Grand total price
    }

    return render(request, 'checkout.html', context)
@csrf_exempt
@login_required
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    grand_total = sum(item.total_price for item in cart_items)
    
    if not cart_items.exists() or grand_total <= 0:
        return JsonResponse({'error': 'No items in cart or invalid total amount'})

    try:
        order = client.order.create(dict(
            amount=int(grand_total * 100),  # Amount in paise
            currency='INR',
            payment_capture='1'
        ))
        return JsonResponse({'id': order['id']})
    except Exception as e:
        return JsonResponse({'error': str(e)})




from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from myapp.models import Cart, OrderDetails, OrderProduct, Payment, FarmerPayment, DeliveryBoy

@csrf_exempt
@login_required
def verify_payment(request):
    data = request.POST
    payment_id = data.get('razorpay_payment_id')
    order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')

    try:
        # Verify the payment signature (replace with your own Razorpay client logic)
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # Retrieve the cart items for the current user
        cart_items = Cart.objects.filter(user=request.user)
        grand_total = sum(item.total_price for item in cart_items)

        if not cart_items.exists():
            return JsonResponse({'status': 'failed', 'error': 'No items in the cart.'})

        # Create a single OrderDetails entry
        order_details = OrderDetails.objects.create(
            user=request.user,
            total_price=grand_total,
            order_status='Pending'
        )

        # Now handle the OrderProduct creation for each product in the cart
        delivery_boy_id = None

        for item in cart_items:
            # Create an OrderProduct entry for each cart item
            OrderProduct.objects.create(
                order=order_details,
                product=item.product,
                quantity=item.quantity
            )

            # Update product stock
            product = item.product
            if product.stock < item.quantity:
                raise Exception(f"Not enough stock for product {product.name}")
            product.stock -= item.quantity
            product.save()

        # Optionally, assign a delivery boy based on criteria like pincode
        delivery_boys = DeliveryBoy.objects.filter(user__pincode=request.user.pincode)
        if delivery_boys.exists():
            delivery_boy_id = delivery_boys.first().id  # Assign the first available delivery boy
        else:
            raise Exception("No delivery boy found for the user's pincode.")

        # Create a FarmerPayment entry only once for the entire order
        FarmerPayment.objects.create(
            user=request.user,
            order_details=order_details,  # Associate with the current order
            date=datetime.now(),
            status='Success',
            delivery_boy_id=delivery_boy_id
        )

        # Create a Payment entry for the overall order
        Payment.objects.create(
            user=request.user,
            order_details=order_details,
            amount_paid=grand_total,
            payment_id=payment_id,
            order_id=order_id,
            status='Success'
        )

        # Clear the user's cart after successful payment
        cart_items.delete()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'failed', 'error': str(e)})





@login_required
def farmer_payment_list(request):
    # Fetch all FarmerPayment records
    farmer_payments = FarmerPayment.objects.all()

    context = {
        'farmer_payments': farmer_payments
    }
    return render(request, 'farmer_payment_list.html', context)

# Function to send OTP email
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
import random

# Function to send OTP email
def send_otp_email(email, otp):
    subject = "Your OTP for Shipment Confirmation"
    message = f"Your OTP for confirming the shipment is: {otp}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# View for confirming shipment
@login_required
def confirm_shipment(request, payment_id):
    payment = get_object_or_404(FarmerPayment, id=payment_id)

    if request.method == "POST":
        # If OTP is already provided by the delivery boy
        if 'otp' in request.POST:
            entered_otp = request.POST.get('otp')
            
            # Verify the OTP stored in the session
            if entered_otp == request.session.get('otp'):
                # Update order status to 'Shipping'
                payment.order_details.order_status = 'Shipping'
                payment.order_details.save()
                
                # Clear OTP from session after successful verification
                del request.session['otp']
                
                messages.success(request, "Order status updated to 'Shipping'.")
                return redirect('farmer_payment_list')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        
        else:
            # Generate and send OTP if 'Ship' button is initially clicked
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp  # Store OTP in session
            user_email = request.POST.get('user_email')
            
            # Send OTP to delivery boy's email
            send_otp_email(user_email, otp)
            
            messages.info(request, "OTP has been sent to the delivery boy's email.")
            return render(request, 'confirm_shipment.html', {'payment_id': payment_id})

    return redirect('farmer_payment_list')


#from myapp.models import Payment, Cart

# Delete all entries from the Payment table
#Payment.objects.all().delete()

# Delete all entries from the Cart table
#Cart.objects.all().delete()
#OrderDetails.objects.all().delete()
#FarmerPayment.objects.all().delete()

@login_required
def success_view(request):
    return render(request, 'success.html')

@login_required
def cancel_view(request):
    return render(request, 'cancel.html')

@login_required
def payment_list(request):
    # Only show payments for the logged-in user
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payment_list.html', {'payments': payments})



@login_required
def payment_detail(request, payment_id):
    # Get the payment object and ensure it belongs to the logged-in user
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payment_detail.html', {'payment': payment})



# Example view function

def admin_payment_detail(request):
    payments = Payment.objects.all()  # Fetch all payments
    deliveryboys = DeliveryBoy.objects.all()  # Fetch delivery boys
    return render(request, 'admin_payment_detail.html', {'payments': payments, 'deliveryboys': deliveryboys})

@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    return redirect('payment_list')  # Redirect to the payment list page

from django.utils import timezone

def assign_delivery(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        
        # Get the payment object (assuming you have a Payment model)
        payment = get_object_or_404(Payment, id=payment_id)

        # Check if a delivery assignment already exists for this payment
        if DeliveryAssignment.objects.filter(payment=payment).exists():
            messages.warning(request, 'This delivery has already been assigned.')
            return redirect('admin_payment_detail')  # Redirect to the same page

        # Get the delivery boys with the same pincode as the customer
        delivery_boys = DeliveryBoy.objects.filter(user__pincode=payment.user.pincode)

        if delivery_boys.exists():
            # For simplicity, let's assign the first delivery boy found (you can add logic to select the best one)
            for delivery_boy in delivery_boys:
                # Count the number of deliveries assigned to this delivery boy today
                today = timezone.now().date()
                assigned_deliveries_today = DeliveryAssignment.objects.filter(
                    delivery_boy=delivery_boy.user,
                    assigned_date__date=today
                ).count()

                # Check if the delivery boy has less than 5 assignments today
                if assigned_deliveries_today < 5:
                    # Create the delivery assignment
                    delivery_assignment = DeliveryAssignment.objects.create(
                        payment=payment,
                        delivery_boy=delivery_boy.user  # Assign the User instance associated with the delivery boy
                    )

                    # Send notification (email, SMS, etc.) to the delivery boy
                    send_delivery_notification(delivery_boy, payment)

                    # Add success message
                    messages.success(request, f'Delivery assigned to {delivery_boy.user.name}.')
                    return redirect('admin_payment_detail')  # Redirect after assigning

            # If no delivery boys are available with less than 5 deliveries
            messages.error(request, 'All delivery boys in this pincode have reached their assignment limit for today.')
        else:
            # No delivery boy found
            messages.error(request, 'No delivery boy found in the customer’s pincode.')

    return render(request, 'admin_payment_detail.html')

@login_required
def deliveryboy_orders(request):
    deliveryboy = request.user  # Assuming the delivery boy is the logged-in user

    # Fetch assignments that are not delivered
    assignments = DeliveryAssignment.objects.filter(
        delivery_boy=deliveryboy
    ).exclude(status='Delivered').select_related('payment', 'payment__user').prefetch_related('payment__order_details__orderproduct_set__product')

    context = {
        'assignments': assignments,
        'delivery_boy_email': deliveryboy.email,  # Pass the delivery boy's email to the context
    }
    
    return render(request, 'deliveryboy_orders.html', context)


@login_required
def send_delivery_notification(delivery_boy, payment):
    # You can implement this logic for email, SMS, etc.
    subject = 'New Delivery Assignment'
    message = f'Dear {delivery_boy.user.name}, you have been assigned a new delivery.'
    recipient = delivery_boy.user.email  # Assuming email is available in the user model
    
    # Send the email (make sure email backend is configured)
    send_mail(subject, message, 'grocery18900@gmail.com', [recipient])

    # Optionally, log or send SMS if needed


@login_required
def my_deliveries(request):
    # Fetch orders delivered by the current logged-in delivery boy
    user = request.user
    delivery_boy = get_object_or_404(DeliveryBoy, user=user)
    
    delivered_orders = DeliveryAssignment.objects.filter(delivery_boy=user, status='Delivered')
    
    return render(request, 'my_deliveries.html', {'delivered_orders': delivered_orders})

@login_required
def delete_order(request, order_id):
    if request.method == 'POST':
        assignment = get_object_or_404(DeliveryAssignment, id=order_id)
        assignment.delete()
        return redirect('deliveryboy_orders')  # Redirect to the orders page
    
@login_required  
def request_otp(request, order_id):
    if request.method == 'POST':
        assignment = get_object_or_404(DeliveryAssignment, id=order_id)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        request.session['otp'] = otp  # Store OTP in session for verification
        request.session['order_id'] = order_id  # Store order ID in session

        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}',
            'from@example.com',  # Replace with your email
            [assignment.payment.user.email],
            fail_silently=False,
        )
        return redirect('deliveryboy_orders')  # Redirect back to orders page

# Function to confirm OTP
@login_required
def confirm_otp(request, order_id):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp'):
            assignment = get_object_or_404(DeliveryAssignment, id=order_id)
            assignment.status = 'Delivered'  # Update status to Delivered
            assignment.save()
            del request.session['otp']  # Clear OTP from session
            del request.session['order_id']  # Clear order ID from session
            messages.success(request, 'Order marked as delivered.')  # Success message
            return redirect('deliveryboy_orders')  # Redirect back to orders page
        else:
            messages.error(request, 'Invalid OTP. Please try again.')  # Error message
            return redirect('deliveryboy_orders')  
        

def farmer_payment_details(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    # Fetch payments for the logged-in user
    farmer_payments = FarmerPayment.objects.filter(user=request.user).select_related('order_details', 'delivery_boy')
    return render(request, 'farmer_payment_details.html', {'farmer_payments': farmer_payments})



# views.py
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib import messages
import joblib
import numpy as np
from PIL import Image
import os

def extract_features(image):
    # Resize the image to a smaller size for faster processing
    image_resized = image.resize((32, 32))  # Resize to 32x32 for simplicity
    mean_color = np.array(image_resized).mean(axis=(0, 1))  # Get mean color (R, G, B)
    return mean_color  # Return the mean color as features

def quality_detect(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        
        # Validate the image type (only allow specific formats)
        if not (image.name.lower().endswith(('.png', '.jpg', '.jpeg'))):
            messages.error(request, 'Only image files (PNG, JPG, JPEG) are allowed.')
            return redirect('quality_detect')  # Redirect back to the quality detect page

        # Check if the image is a fruit or vegetable based on the file name
        allowed_keywords = ['apple', 'banana', 'orange', 'grapes', 'carrot', 'tomato', 'potato', 'lettuce', 'cucumber', 'pepper','gap','banana']
        if not any(keyword in image.name.lower() for keyword in allowed_keywords):
            messages.error(request, 'Please upload an image of a fruit or vegetable only.')
            return redirect('quality_detect')  # Redirect back to the quality detect page

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        # Load your machine learning model
        model_path = os.path.join('myapp', 'models', 'model.pkl')  # Correct path to your model
        model = joblib.load(model_path)

        # Preprocess the image for prediction
        img = Image.open(image)  # Open the image using Pillow
        img_array = np.array(img)  # Convert to numpy array

        # Extract features from the image
        features = extract_features(img)  # Use the extract_features function

        # Make prediction
        prediction = model.predict([features])  # Pass the features as a 2D array

        # Convert prediction to readable format
        prediction_text = "Fresh" if prediction[0] == 1 else "Not Fresh"

        # Prepare explanation for not fresh products
        explanation = []
        detailed_features = []

        if prediction[0] == 0:  # If not fresh
            explanation.append("The product is not fresh due to the following signs of spoilage:")

            # Check if there are additional outputs
            if len(prediction) > 1:
                if prediction[1] > 0.5:  # Discoloration
                    detailed_features.append("Discoloration observed, indicating potential spoilage.")
                if prediction[2] > 0.5:  # Damage
                    detailed_features.append("Visible damage detected, which can lead to spoilage.")
                if prediction[3] > 0.5:  # Mold
                    detailed_features.append("Mold present on the surface, a clear sign of spoilage.")
                if prediction[4] > 0.5:  # Softness
                    detailed_features.append("Soft or mushy texture detected, indicating overripeness.")
                if prediction[5] > 0.5:  # Odor
                    detailed_features.append("Unpleasant odor detected, suggesting spoilage.")
                if prediction[6] > 0.5:  # Wrinkling
                    detailed_features.append("Wrinkling or shriveling observed, indicating dehydration.")
                if prediction[7] > 0.5:  # Excessive moisture
                    detailed_features.append("Excessive moisture or wetness detected, which can promote spoilage.")
                if prediction[8] > 0.5:  # Color fading
                    detailed_features.append("Fading color observed, indicating deterioration.")
                if prediction[9] > 0.5:  # Unusual spots
                    detailed_features.append("Unusual spots or blemishes detected, which may indicate spoilage.")
                if prediction[10] > 0.5:  # Separation of layers (for packaged products)
                    detailed_features.append("Separation of layers in packaged products detected, indicating spoilage.")

        # Combine the explanation and detailed features correctly
        if detailed_features:
            explanation.append(" ".join(detailed_features))  # Join the detailed features into a single string
        else:
            explanation.append("No specific spoilage signs detected.")

        # Join the explanation list into a single string for rendering
        final_explanation = " ".join(explanation)

        return render(request, 'quality_result.html', {
            'uploaded_file_url': uploaded_file_url,
            'prediction': prediction_text,
            'explanation': final_explanation  # Pass the final explanation to the template
        })
    return render(request, 'quality_detect.html')