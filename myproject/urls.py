from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
     path('custom_admin/', include('myapp.urls')), 
    
    
    
    
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    
    path('services/', views.services, name='services'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
     path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/deliveryboy/', views.deliveryboy_dashboard, name='deliveryboy_dashboard'),
    
      path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
   path('custom_admin/product/', views.admin_product_view, name='admin_product_view'),
    
    
    path('check_email/', views.check_email, name='check_email'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    
     path('logout/', views.logout_view, name='logout'),
    
   path('manage-users/', views.manage_users, name='manage_users'),
    path('filter-users/<str:role>/', views.filter_users, name='filter_users'),
   path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    
 path('profile/', views.all_users_view, name='profile'),
  path('edit-profile/', views.edit_profile_view, name='edit_profile'),
  
  
     path('farmer/profile/', views.farmer_profile_view, name='farmer_profile'),
     
 path('edit-farmer-profile/', views.farmer_profile_edit_view, name='farmer_profile_edit'),
    
      path('deliveryboy/profile/', views.deliveryboy_profile_view, name='deliveryboy_profile'),
      path('deliveryboy/profile/edit/',views.deliveryboy_profile_edit_view, name='deliveryboy_profile_edit'),


      path('add_category/', views.add_category, name='add_category'),
    path('list_categories/', views.list_categories, name='list_categories'),
     path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
   path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('view_subcategories/', views.view_subcategories, name='view_subcategories'),
     path('edit_subcategory/<int:id>/', views.edit_subcategory, name='edit_subcategory'),
    path('delete_subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
   
   

 path('add_product_category/', views.add_product_category, name='add_product_category'),
    path('view_product_categories/', views.view_product_categories, name='view_product_categories'),
    path('edit_product_category/<int:id>/', views.edit_product_category, name='edit_product_category'),
    path('delete_product_category/<int:id>/', views.delete_product_category, name='delete_product_category'),
    
    
    
    
    path('add_product/', views.add_product, name='add_product'),
    path('list_products/', views.list_products, name='list_products'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    
     path('products/', views.list_category_products, name='list_category_products'),
     path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    
            path('contact/', views.contact_view, name='contact'),
            
              path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
     path('wishlist/', views.wishlist_view, name='wishlist'),
      path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
     
       path('product/<int:product_id>/', views.product_details, name='product_details'),
       
    
 path('add_price_chart/', views.add_price_chart, name='add_price_chart'),
    path('view_price_charts/', views.view_price_charts, name='view_price_charts'),
    
    path('edit_price_chart/<int:pk>/', views.edit_price_chart, name='edit_price_chart'),
    path('delete_price_chart/<int:pk>/', views.delete_price_chart, name='delete_price_chart'),
            
          path('price_chart_customer/', views.price_chart_customer, name='price_chart_customer'),
          
          
           path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view-cart/', views.view_cart, name='view_cart'),
     path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
      path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
       path('update-cart/', views.update_cart, name='update_cart'),
          
            path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
                   path('compare_prices/', views.compare_product_prices, name='compare_prices'),
path('checkout/', views.checkout_view, name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
     path('payments/', views.payment_list, name='payment_list'),
      path('payment/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
      path('admin_payment_detail/', views.admin_payment_detail, name='admin_payment_detail'), 
   
path('farmer/payment-list/', views.farmer_payment_list, name='farmer_payment_list'),

       path('assign-delivery/', views.assign_delivery, name='assign_delivery'),

        path('deliveryboy/orders/', views.deliveryboy_orders, name='deliveryboy_orders'),  # New URL pattern
         path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
         path('request_otp/<int:order_id>/', views.request_otp, name='request_otp'),
    path('confirm_otp/<int:order_id>/', views.confirm_otp, name='confirm_otp'),
      path('my_deliveries/', views.my_deliveries, name='my_deliveries'),
       path('quality_detect/', views.quality_detect, name='quality_detect'),
       path('confirm-shipment/<int:payment_id>/', views.confirm_shipment, name='confirm_shipment'),
   
     path('submit-feedback/<int:payment_id>/', views.submit_feedback_rating, name='submit_feedback_rating'),
 path('feedback-list/', views.feedback_list, name='feedback_list'),
  path('feedback_farm/', views.feedback_farm_view, name='feedback_farm'),
      path('education/dashboard/', views.education_dashboard, name='education_dashboard'),  # New URL for education dashboard
path('edcat-category/', views.edcat_category, name='edcat_category'), 
    path('categories/', views.view_categories, name='view_categories'),
  path('categories/update/<int:category_id>/', views.update_category, name='update_category'), 
    path('categories/remove/<int:category_id>/', views.remove_category, name='remove_category'),
 path('create-material/', views.material_create, name='create_material'),
   path('material-list/', views.material_list, name='material_list'),  # Add this line
    path('materials/edit/<int:material_id>/', views.edit_material, name='edit_material'),
    path('materials/delete/<int:material_id>/', views.delete_material, name='delete_material'),
    path('farm-materials/', views.farmmaterial_view, name='farmmaterial_view'),
    path('product-price-details/', views.product_price_details_view, name='product_price_details'),
    path('trends/', views.trends_dashboard, name='trends'),
    
    path('sales-performance-data/', views.sales_performance_data, name='sales_performance_data'),
    path('seasonal_category/', views.add_seasonal_category, name='seasonal_category'),
    path('list_seasonal_categories/', views.list_seasonal_categories, name='list_seasonal_categories'),
      path('seasonal_product/', views.add_seasonal_product, name='seasonal_product'),
         path("check-product-exists/", views.check_product_exists, name="check_product_exists"),
    path('list_seasonal_products/', views.list_seasonal_products, name='list_seasonal_products'),
    path('edit-seasonal-category/<int:category_id>/', views.edit_seasonal_category, name='edit_seasonal_category'),
  path('delete-seasonal-category/<int:category_id>/', views.delete_seasonal_category, name='delete_seasonal_category'),
 path('edit_seasonal_product/<int:product_id>/', views.edit_seasonal_product, name='edit_seasonal_product'),
    path('delete-product/<int:product_id>/', views.delete_seasonal_product, name='delete_seasonal_product'),
     path('seasonal/', views.seasonal_page, name='seasonal_page'),
       path('add-event/', views.add_event, name='add_event'),
       path('events/', views.event_list, name='event_list'),
       path('farmer-event/', views.farmer_event, name='farmer_event'),
path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('register-event/<int:event_id>/', views.register_event, name='register_event'),
       path('verify-otp/', views.verify_otps, name='verify_otps'),  # Updated URL name
  path('events/<int:event_id>/registered/', views.view_registered_people, name='view_registered_people'),
  path('send_email/', views.send_email, name='send_email'),
   
     path('add_disease/', views.add_disease, name='add_disease'),
    path('view_diseases/', views.view_diseases, name='view_diseases'),
    path('edit_disease/<int:id>/', views.edit_disease, name='edit_disease'),
    path('delete_disease/<int:id>/', views.delete_disease, name='delete_disease'),
    path('farmer-disease/', views.farmer_disease, name='farmer_disease'),
 
    
    
      path('payment-table/', views.payment_table_view, name='payment_table'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)