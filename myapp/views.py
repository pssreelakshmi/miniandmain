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
from .models import Cart, Payment, DeliveryAssignment, OrderDetails,FarmerPayment,Feedback,Rating



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



from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User  # Ensure you have the correct import for your User model

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Check for admin credentials
        if email == 'admin@gmail.com' and password == 'Admin@123':
            return redirect('admin_dashboard')

        # Check for education module credentials
        if email == 'education@gmail.com' and password == 'Education@123':
            return redirect('education_dashboard')
            # Create a user object for the education module
           
        # Authenticate existing users
        try:
            user = User.objects.get(email=email, password=password)
            login(request, user)  # Use Django's login function
            
            # Redirect based on user role
            if user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            elif user.role == 'deliveryboy':
                return redirect('deliveryboy_dashboard')
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')


def education_dashboard(request):
    return render(request, 'education_dashboard.html')  # Render the education dashboard template
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
from .models import EventRegistration


# Delete all entries from the Payment table
#Payment.objects.all().delete()

# Delete all entries from the Cart table
#Cart.objects.all().delete()
#OrderDetails.objects.all().delete()
#FarmerPayment.objects.all().delete()
#Feedback.objects.all().delete()
#Rating.objects.all().delete()
#EventRegistration.objects.all().delete()

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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from .models import DeliveryAssignment, Payment



@login_required
def deliveryboy_orders(request):
    deliveryboy = request.user  # Assuming the delivery boy is the logged-in user

    # Fetch assignments that are not delivered
    assignments = DeliveryAssignment.objects.filter(
        delivery_boy=deliveryboy
    ).exclude(status='Delivered').select_related('payment', 'payment__user')

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
        allowed_keywords = ['apple', 'banana', 'orange', 'grapes', 'carrot', 'tomato', 'potato', 'lettuce', 'cucumber', 'pepper','gap','banana','abc']
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


from django.shortcuts import render, redirect, get_object_or_404
from .models import Feedback, Rating, Payment

def submit_feedback_rating(request, payment_id):
    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        rating_value = request.POST.get("rating")

        # Fetch payment and related order details
        payment = get_object_or_404(Payment, id=payment_id)
        order_details = payment.order_details

        # Ensure order_details is present
        if not order_details:
            return render(request, 'error.html', {'message': 'Order details not found for this payment.'})

        # Fetch related product(s)
        products = order_details.products  # Corrected from 'product' to 'products'

        # Assuming you want to save feedback for each product
        for product in products.all():  # Adjust if 'products' is a related manager
            # Save feedback
            Feedback.objects.create(
                payment=payment,
                user=request.user,
                product=product,
                feedback_text=feedback_text
            )
            
            # Save rating
            Rating.objects.create(
                payment=payment,
                user=request.user,
                product=product,
                rating_value=rating_value
            )

        # Redirect to a success page or back to payment details
        return redirect('payment_detail', payment_id=payment_id)  # Adjust the redirect as necessary
    
    return render(request, 'payment_details.html')


from django.shortcuts import render
from .models import Feedback, Rating

def feedback_list(request):
    # Fetch all feedback and rating data
    feedbacks = Feedback.objects.select_related('user', 'product', 'payment', 'product__farmer').all()
    ratings = Rating.objects.select_related('user', 'product', 'payment', 'product__farmer').all()

    # Render the feedback list template
    return render(request, 'feedback_list.html', {
        'feedbacks': feedbacks,
        'ratings': ratings,
    })


from django.shortcuts import render

def feedback_farm_view(request):
    feedbacks = Feedback.objects.all()
    ratings = Rating.objects.all()
    return render(request, 'feedback_farm.html', {'feedbacks': feedbacks, 'ratings': ratings})



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EdCat
import re
from django.db.models import Q

def edcat_category(request):
    if request.method == 'POST':
        catname = request.POST.get('catname').strip()  # Get and strip whitespace

        if not catname:
            error_message = "Category name is required."
            return render(request, 'edadd_category.html', {'error_message': error_message})

        # Case-insensitive and whitespace-insensitive duplicate check
        if EdCat.objects.filter(Q(catname__iexact=catname) | Q(catname__icontains=catname)).exists():
            error_message = "This category already exists ."
            return render(request, 'edadd_category.html', {'error_message': error_message})


        if not re.match("^[a-zA-Z ]+$", catname):
            error_message = "Category name must only contain letters and spaces."
            return render(request, 'edadd_category.html', {'error_message': error_message})

        EdCat.objects.create(catname=catname)
        messages.success(request, "Category added successfully!")
        return redirect('edcat_category')

    categories = EdCat.objects.all()
    return render(request, 'edadd_category.html', {'categories': categories})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import EdCat

# View all categories
def view_categories(request):
    categories = EdCat.objects.all()  # Fetch all categories from the EdCat table
    return render(request, 'view_categories.html', {'categories': categories})

# Remove/Delete category
def remove_category(request, category_id):
    category = get_object_or_404(EdCat, catid=category_id)  # Get the category by ID
    category.delete()  # Remove the category from the database
    messages.success(request, 'Category removed successfully.')  # Show success message
    return redirect('view_categories')  # Redirect back to the categories list

# Update/Edit category
def update_category(request, category_id):  # Ensure the function accepts category_id
    category = get_object_or_404(EdCat, catid=category_id)  # Get the category by ID

    if request.method == 'POST':
        catname = request.POST.get('catname')  # Get the updated category name from the form
        
        # Check if the category name already exists
        if EdCat.objects.filter(catname=catname).exclude(catid=category_id).exists():
            messages.error(request, 'Category name already exists. Please choose a different name.')  # Show error message
            return render(request, 'update_category.html', {'category': category})  # Render the form again with the existing category

        if catname:  # Check if the category name is provided
            category.catname = catname  # Update the category name
            category.save()  # Save the changes to the database
            messages.success(request, 'Category updated successfully.')  # Show success message
            return redirect('view_categories')  # Redirect back to the categories list
        else:
            messages.error(request, 'Category name cannot be empty.')  # Show error message

    return render(request, 'update_category.html', {'category': category})  # Render the update form


from django.shortcuts import render, redirect
from .models import Material, EdCat
from django.http import HttpResponse

def material_create(request):
    if request.method == 'POST':
        # Handling form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        # Handling the image
        image = request.FILES.get('image')

        # Create a new material object and save it to the database
        new_material = Material(
            title=title,
            description=description,
            content=content,
            category_id=category_id,
            image=image,
        )
        new_material.save()

        # Redirect to the material list page after saving the new material
        return redirect('material_list')  # Adjust the URL name based on your project

    # Get all categories from EdCat table
    categories = EdCat.objects.all()

    # Render the create material form if the method is GET
    return render(request, 'create_material.html', {'categories': categories})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Material


def material_list(request):
    materials = Material.objects.all()  # Get all materials from the database
    return render(request, 'material_list.html', {'materials': materials})

# View for editing a material
from django.shortcuts import render, get_object_or_404, redirect
from .models import Material, EdCat

def edit_material(request, material_id):
    # Get the material object to edit using the correct field name (material_id)
    material = get_object_or_404(Material, material_id=material_id)

    if request.method == 'POST':
        # Get the form values
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        category_name = request.POST.get('category')  # The name of the selected category

        # Get the EdCat instance corresponding to the category
        category = EdCat.objects.get(catname=category_name)

        # Handle the image (optional)
        image = request.FILES.get('image')
        
        # Update the material object
        material.title = title
        material.description = description
        material.content = content
        material.category = category  # Assign the EdCat instance
        if image:
            material.image = image
        
        # Save the updated material object
        material.save()

        # Redirect to material list or another page
        return redirect('material_list')  # Adjust this URL name based on your project

    # Get all categories to populate the dropdown in the form
    categories = EdCat.objects.all()

    # Render the edit material form
    return render(request, 'edit_material.html', {'material': material, 'categories': categories})

# View for deleting a material
def delete_material(request, material_id):
    material = get_object_or_404(Material, material_id=material_id)  # Get material by ID
    if request.method == 'POST':
        material.delete()  # Delete the material from the database
        return redirect('material_list')  # Redirect to the materials list page

    return render(request, 'delete_material.html', {'material': material})

from django.shortcuts import render
from .models import Material, EdCat

def farmmaterial_view(request):
    category_id = request.GET.get('category')  # Get selected category from URL
    categories = EdCat.objects.all()  # Fetch all categories
    
    if category_id:
        materials = Material.objects.filter(category_id=category_id)  # Filter materials by category
    else:
        materials = Material.objects.all()  # Fetch all materials if no category is selected
    
    return render(request, 'farmmaterial_view.html', {'materials': materials, 'categories': categories, 'selected_category': category_id})


from django.shortcuts import render
from .models import Price_Chart

def product_price_details_view(request):
    # Retrieve all price chart entries
    price_charts = Price_Chart.objects.all()

    return render(request, 'product_price_details.html', {'price_charts': price_charts})

from django.shortcuts import render

def trends_dashboard(request):
    return render(request, 'trends.html')

from django.http import JsonResponse
from django.db.models import Sum
from myapp.models import OrderDetails, Product

def sales_performance_data(request):
    sales_data = (
        OrderDetails.objects
        .values('product__name')  # Group by product name
        .annotate(total_sales=Sum('quantity'))  # Sum of quantity sold
        .order_by('-total_sales')  # Order by most sold products
    )

    labels = [item['product__name'] for item in sales_data]
    data = [item['total_sales'] for item in sales_data]

    return JsonResponse({'labels': labels, 'data': data})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SeasonalCategory
import re
from django.db.models import Q

def add_seasonal_category(request):
    if request.method == "POST":
        month_name = request.POST.get('month_name').strip()  # Strip whitespace

        if not month_name:
            messages.error(request, "Month name is required.")
            return render(request, 'seasonal_category.html')  # Re-render the form

        # Case-insensitive and whitespace-insensitive duplicate check
        if SeasonalCategory.objects.filter(Q(month_name__iexact=month_name) | Q(month_name__icontains=month_name)).exists():
            messages.error(request, "This month category already exists.")
            return render(request, 'seasonal_category.html')

        if not re.match("^[a-zA-Z ]+$", month_name):
            messages.error(request, "Month name must only contain letters and spaces.")
            return render(request, 'seasonal_category.html')

        SeasonalCategory.objects.create(month_name=month_name)
        messages.success(request, "Seasonal category added successfully.")
        return redirect('seasonal_category')  # Redirect after successful creation

    return render(request, 'seasonal_category.html')


def list_seasonal_categories(request):
    categories = SeasonalCategory.objects.all()
    return render(request, 'list_seasonal_categories.html', {'categories': categories})


def edit_seasonal_category(request, category_id):
    category = get_object_or_404(SeasonalCategory, id=category_id)
    if request.method == "POST":
        new_month_name = request.POST.get("month_name")
        category.month_name = new_month_name
        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect('list_seasonal_categories')
    return render(request, 'edit_seasonal_category.html', {'category': category})

def delete_seasonal_category(request, category_id):
    category = get_object_or_404(SeasonalCategory, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('list_seasonal_categories')

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SeasonalCategory, SeasonalProduct

from django.shortcuts import render, redirect
from .models import SeasonalCategory, SeasonalProduct
from django.db.models import Q
import re

def add_seasonal_product(request):
    categories = SeasonalCategory.objects.all()

    if request.method == "POST":
        category_id = request.POST.get('category_id')
        product_names = request.POST.getlist('product_name')  # Get list of product names
        descriptions = request.POST.getlist('description')  # Get list of descriptions
        images = request.FILES.getlist('image')  # Get list of images

        category = SeasonalCategory.objects.get(id=category_id)

        for i in range(len(product_names)):
            product_name = product_names[i].strip()  # Strip whitespace from product name
            description = descriptions[i].strip() if i < len(descriptions) else ""  # Handle missing descriptions
            image = images[i] if i < len(images) else None  # Handle missing images

            if not product_name:  # Check for empty product name
                return render(request, 'seasonal_product.html', {
                    'categories': categories,
                    'error_message': "Product name is required."
                })

            # Case-insensitive and whitespace-insensitive duplicate check within the same category
            if SeasonalProduct.objects.filter(
                Q(product_name__iexact=product_name) | Q(product_name__icontains=product_name),
                category=category
            ).exists():
                return render(request, 'seasonal_product.html', {
                    'categories': categories,
                    'error_message': f"The product '{product_name}' already exists in this category."
                })

            if not re.match("^[a-zA-Z0-9 ]+$", product_name): # Validation for product name
                return render(request, 'seasonal_product.html', {
                    'categories': categories,
                    'error_message': f"The product name '{product_name}' contains invalid characters. Only letters, numbers and spaces are allowed."
                })


            SeasonalProduct.objects.create(
                category=category,
                product_name=product_name,
                description=description,
                image=image
            )

        return redirect('list_seasonal_products')

    return render(request, 'seasonal_product.html', {'categories': categories})

@csrf_exempt
def check_product_exists(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_name = data.get("product_name", "").strip()
        category_id = data.get("category_id", "").strip()

        if SeasonalProduct.objects.filter(product_name__iexact=product_name, category_id=category_id).exists():
            return JsonResponse({"exists": True})
        else:
            return JsonResponse({"exists": False})


from django.shortcuts import render, redirect, get_object_or_404
from .models import SeasonalProduct, Category

def list_seasonal_products(request):
    products = SeasonalProduct.objects.all()
    return render(request, 'list_seasonal_products.html', {'products': products})

from django.shortcuts import render, get_object_or_404, redirect
from.models import SeasonalProduct, SeasonalCategory
from django.db.models import Q
import re

def edit_seasonal_product(request, product_id):
    product = get_object_or_404(SeasonalProduct, id=product_id)
    categories = SeasonalCategory.objects.all()

    if request.method == "POST":
        product_name = request.POST.get('product_name').strip()  # Strip whitespace
        category_id = request.POST.get('category_id')
        description = request.POST.get('description', '').strip()  # Strip whitespace from description
        image = request.FILES.get('image')  # Get the new image if uploaded

        category = get_object_or_404(SeasonalCategory, id=category_id)

        if not product_name:
            error_message = "Product name is required."
            return render(request, 'edit_seasonal_product.html', {
                'product': product,
                'categories': categories,
                'error_message': error_message
            })

        # Case-insensitive and whitespace-insensitive duplicate check (excluding the current product)
        if SeasonalProduct.objects.filter(
            Q(product_name__iexact=product_name) | Q(product_name__icontains=product_name),
            category=category
        ).exclude(id=product_id).exists():  # Exclude the current product from the duplicate check
            error_message = f"The product '{product_name}' already exists in this category."
            return render(request, 'edit_seasonal_product.html', {
                'product': product,
                'categories': categories,
                'error_message': error_message
            })

        if not re.match("^[a-zA-Z0-9 ]+$", product_name): # Validation for product name
            error_message = f"The product name '{product_name}' contains invalid characters. Only letters, numbers and spaces are allowed."
            return render(request, 'edit_seasonal_product.html', {
                'product': product,
                'categories': categories,
                'error_message': error_message
            })

        product.product_name = product_name
        product.category = category
        product.description = description  # Update description

        if image:  # Update image only if a new one is uploaded
            product.image = image

        product.save()

        return redirect('list_seasonal_products')

    return render(request, 'edit_seasonal_product.html', {'product': product, 'categories': categories})


def delete_seasonal_product(request, product_id):
    product = get_object_or_404(SeasonalProduct, id=product_id)
    product.delete()
    return redirect('list_seasonal_products')

# views.py

# views.py

# views.py

from django.shortcuts import render
from .models import SeasonalProduct, SeasonalCategory

def seasonal_page(request):
    # Get selected category from the GET request
    selected_category = request.GET.get('category')
    categories = SeasonalCategory.objects.all()  # Fetch all categories
    
    if selected_category:
        # Filter products based on the selected category
        products = SeasonalProduct.objects.filter(category__id=selected_category)
        selected_category_obj = SeasonalCategory.objects.get(id=selected_category)
        selected_category_name = selected_category_obj.month_name  # Get the name of the selected category
    else:
        products = SeasonalProduct.objects.none()  # No products if no category is selected
        selected_category_name = None  # Set to None if no category is selected
    
    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'seasonal_page.html', context)



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Event
from datetime import datetime

def add_event(request):
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')  # Handling file upload
        description = request.POST.get('description')
        registration_start_date = request.POST.get('registration_start_date')
        registration_end_date = request.POST.get('registration_end_date')
        event_date = request.POST.get('event_date')
        mode = request.POST.get('mode')

        # Basic Validation
        if not all([name, image, description, registration_start_date, registration_end_date, event_date, mode]):
            messages.error(request, "All fields are required.")
            return redirect('add_event')

        if registration_start_date > registration_end_date:
            messages.error(request, "Registration start date must be before the end date.")
            return redirect('add_event')

        # Save Event
        Event.objects.create(
            name=name,
            image=image,
            description=description,
            registration_start_date=registration_start_date,
            registration_end_date=registration_end_date,
            event_date=event_date,
            mode=mode
        )
        messages.success(request, "Event added successfully!")
        return redirect('add_event')  # Redirect to prevent form resubmission

    return render(request, 'add_event.html')

from django.shortcuts import render
from .models import Event
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from .models import Event

from django.shortcuts import render, get_object_or_404
from .models import Event, EventRegistration  # Import your models

def event_list(request):
    events = Event.objects.all()  # Fetch all events from the database
    return render(request, 'event_list.html', {'events': events})

def view_registered_people(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    registrations = EventRegistration.objects.filter(event=event) # Fetch registrations for this event

    return render(request, 'registered_people.html', {'event': event, 'registrations': registrations})

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == "POST":
        event.name = request.POST['name']
        event.description = request.POST['description']
        event.registration_start_date = request.POST['registration_start_date']
        event.registration_end_date = request.POST['registration_end_date']
        event.event_date = request.POST['event_date']
        event.mode = request.POST['mode']
        
        if 'image' in request.FILES:
            if event.image:
                default_storage.delete(event.image.path)
            event.image = request.FILES['image']
        
        event.save()
        return redirect('event_list')

    return render(request, 'edit_event.html', {'event': event})

# Delete Event
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.image:
        default_storage.delete(event.image.path)
    event.delete()
    return redirect('event_list')



from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, EventRegistration
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import random
from datetime import date

def farmer_event(request):
    today = date.today()  # Get today's date
    events = Event.objects.all()  # Fetch all events (You can filter if needed)

    # Check if the user has already registered for each event
    registered_events = []
    if request.user.is_authenticated:  # Assuming you have user authentication
        registered_events = EventRegistration.objects.filter(email=request.user.email).values_list('event_id', flat=True)
    
    return render(request, 'farmer_event.html', {
        'events': events,
        'today': today,
        'registered_events': registered_events,  # Pass registered event IDs to the template
    })

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def register_event(request, event_id):
    """Handles event registration and sends OTP via email."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Validate inputs
        if not all([name, email, phone]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

        try:
            event = Event.objects.get(id=event_id)  # Ensure event exists
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid event ID.'}, status=400)

        # Check if the user has already registered for this event
        if EventRegistration.objects.filter(event_id=event_id, email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already registered for this event.'}, status=400)

        # Generate OTP
        otp = generate_otp()

        # Store data in session
        request.session['otp'] = otp
        request.session['event_id'] = event_id
        request.session['name'] = name
        request.session['email'] = email
        request.session['phone'] = phone

        # Send OTP via email
        send_mail(
            'Event Registration OTP',
            f'Your OTP for event registration is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'OTP sent to your email.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def verify_otps(request):
    """Verifies the OTP and registers the user for the event."""
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        if user_otp == stored_otp:
            # Retrieve stored session data
            event_id = request.session.get('event_id')
            name = request.session.get('name')
            email = request.session.get('email')
            phone = request.session.get('phone')

            try:
                event = Event.objects.get(id=event_id)
                # Save data to EventRegistration table with status 'pending'
                EventRegistration.objects.create(
                    event=event,
                    name=name,
                    email=email,
                    phone=phone,
                    status='pending'  # Set status to 'pending'
                )

                # Send confirmation email
                send_mail(
                    'Event Registration Successful',
                    'You have successfully registered for the event. The event details will be shared soon.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                # Clear session data
                for key in ['otp', 'event_id', 'name', 'email', 'phone']:
                    request.session.pop(key, None)

                return JsonResponse({'status': 'success', 'message': 'Registration successful.'})

            except Event.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid event ID.'}, status=400)

        return JsonResponse({'status': 'error', 'message': 'Invalid OTP.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


from django.http import JsonResponse
from django.core.mail import send_mail

def send_email(request):
    """Handles sending emails and updating status to 'delivered'."""
    if request.method == 'POST':
        emails = request.POST.get('emails').split(',')
        link = request.POST.get('link')
        subject = request.POST.get('subject')

        for email in emails:
            # Send email
            send_mail(
                subject,
                f'Here is the link for the event: {link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Update status to 'delivered'
            EventRegistration.objects.filter(email=email).update(status='delivered')

        return JsonResponse({'status': 'success', 'message': 'Emails sent successfully.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
    
    
    
    
    
# Delete all entries from the Payment table
#Payment.objects.all().delete()

# Delete all entries from the Cart table
#Cart.objects.all().delete()
#OrderDetails.objects.all().delete()
#FarmerPayment.objects.all().delete()
#Feedback.objects.all().delete()
#Rating.objects.all().delete()
#Rating.objects.all().delete()
#EventRegistration.objects.all().delete()

# Import the Plant model
#from myapp.models import Plant

# Delete all entries from the Plant model
#Plant.objects.all().delete()


from django.shortcuts import render

def upload_image(request):
    return render(request, 'upload_image.html')



# views.py
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import PlantDisease
from django.shortcuts import render, redirect
from .models import PlantDisease
from django.core.exceptions import ValidationError
import re

def add_disease(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        tips_to_control = request.POST.get('tips_to_control')  # New field

        # Validate title: it should not contain numbers
        if title and re.search(r'\d', title):  # Title contains numbers
            return render(request, 'add_disease.html', {'error': 'Title should not contain numbers.'})
        
        # Validate image: should not be a PDF
        if image:
            allowed_image_types = ['image/jpeg', 'image/png', 'image/jpg']
            if image.content_type not in allowed_image_types:
                return render(request, 'add_disease.html', {'error': 'Please upload a valid image (JPG, PNG). PDF is not allowed.'})
        
        # If title, image, description, and tips_to_control are provided and valid
        if title and image and description and tips_to_control:
            PlantDisease.objects.create(
                title=title,
                image=image,
                description=description,
                tips_to_control=tips_to_control  # New field
            )
            return redirect('view_diseases')  # Redirect to the disease list page after saving

        # If any field is missing or invalid
        return render(request, 'add_disease.html', {'error': 'All fields are required.'})

    return render(request, 'add_disease.html')  # Initial GET request rendering


def view_diseases(request):
    diseases = PlantDisease.objects.all()
    return render(request, 'view_diseases.html', {'diseases': diseases})

from django.core.exceptions import ValidationError

def edit_disease(request, id):
    disease = get_object_or_404(PlantDisease, id=id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        tips_to_control = request.POST.get('tips_to_control')  # New field
        
        # Validate title - Ensure no numbers in the title
        if any(char.isdigit() for char in title):
            return render(request, 'edit_disease.html', {
                'disease': disease,
                'error_message': 'Title should not contain numbers.'
            })
        
        # Validate image type
        if 'image' in request.FILES:
            image = request.FILES['image']
            if not image.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
                return render(request, 'edit_disease.html', {
                    'disease': disease,
                    'error_message': 'Please upload a valid image (JPG, PNG).'
                })
            disease.image = image
        
        # Update fields
        disease.title = title
        disease.description = description
        disease.tips_to_control = tips_to_control  # New field
        disease.save()
        return redirect('view_diseases')
    
    return render(request, 'edit_disease.html', {'disease': disease})

def delete_disease(request, id):
    disease = get_object_or_404(PlantDisease, id=id)
    if request.method == 'POST':
        disease.delete()
    return redirect('view_diseases')



from django.shortcuts import render
from .models import PlantDisease

def farmer_disease(request):
    # Fetch all PlantDisease records from the database
    diseases = PlantDisease.objects.all()
    
    # Pass the data to the template
    return render(request, 'farmer_disease.html', {'diseases': diseases})



from django.shortcuts import render
from django.http import HttpResponse
from .models import Payment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def payment_table_view(request):
    payments = Payment.objects.all()
    return render(request, 'payment_table.html', {'payments': payments})

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Payment

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Payment

def download_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payments.pdf"'

    # Create a PDF document
    pdf = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    title = Paragraph("Payment Data Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))  # Add space after the title

    # Fetch all payment data
    payments = Payment.objects.all()

    # Create a list of lists for the table data
    data = [['User Email', 'Products', 'Amount Paid', 'Payment ID', 'Order ID', 'Order Status', 'Created At']]
    for payment in payments:
        # Get product names
        if payment.order_details:
            product_names = ", ".join([str(product.product_name) for product in payment.order_details.products.all()])
        else:
            product_names = "No products"

        # Get order status
        order_status = payment.order_details.order_status if payment.order_details else "Unknown"

        # Append the row to the data
        data.append([
            payment.user.email,
            product_names,
            f"Rs.{payment.amount_paid:.2f}",  # Format amount as currency
            payment.payment_id,
            payment.order_id,
            order_status,
            payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007BFF')),  # Header row background (blue)
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),  # Table body background (light gray)
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),  # Add grid lines (light gray)
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size for all cells
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Table body text color
    ]))

    elements.append(table)
    pdf.build(elements)

    return response