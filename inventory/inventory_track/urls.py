

from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import get_models,master_dashboard
urlpatterns = [
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),  # Master kullanıcı login
    path('admin_dashboard/<str:company_code>/', views.admin_dashboard, name='admin_dashboard'),  # Master kullanıcı login
    # path('login', views.company_login, name='company_login'),
    path('master_login/', views.master_login, name='master_login'),  # Master kullanıcı login
    path('ldap-login/', views.ldap_login_view, name='ldap_login'),  # LDAP kullanıcı login
    # path('master-dashboard/', views.master_dashboard, name='master_dashboard'),
    path('create-user-from-settings/', views.create_custom_user_from_settings, name='create_user_from_settings'),
    path('create/', views.create_company, name='create_company'),
    path('list_users/<str:company_code>/', views.list_users, name='list_users'),
    path('create_user/<str:company_code>',views.create_user,name="create_user"),
    path('company_dashboard/<str:company_code>/', views.company_dashboard, name='company_dashboard'),
    path('sync_ldap_groups_and_users/<int:company_id>', views.get_all_ldap_users_and_groups, name='sync_ldap_groups_and_users'),
    path('master_dashboard/<str:company_code>', master_dashboard, name='master_dashboard'),
    # path('company_login/', views.company_login, name='company_login'),
    # path('custom_user_login/',views.custom_login,name="custom_user_login"),
    path('edit_ldap_config/<str:company_code>', views.edit_ldap_config, name='edit_ldap_config'),
    # Ekleme işlemleri
    path('create_product/<str:company_code>', views.create_product, name='create_product'),
    path('product_page/<str:company_code>', views.product_page, name='product_page'),
    path('inventory/<str:company_code>', views.inventory, name='inventory'),
    #add
    path('add-category/<str:company_code>', views.add_category, name='add_category'),
    path('add-product-status/<str:company_code>', views.add_product_status_view, name='add-product-status'),
    path('add-brand/<str:company_code>', views.add_brand_view, name='add_brand'),
    path('add-model/<str:company_code>', views.add_model_view, name='add_model'),
    path('manage_entities/<str:company_code>', views.manage_entities_view, name='manage_entities'),
    # get 
    path('get-brands/<str:company_code>', views.get_brands, name='get_brands'),
    path('get_products/<str:company_code>', views.get_products, name='get_products'),
    # path('get-status/<str:company_code>', views.get_product_statuses, name='get_status'),
    path('get-models/<str:company_code>', views.get_models, name='get_models'),
    # path('get-categories/<str:company_code>', views.get_categories, name='get_categories'),
    path('asset_assignment_view/<str:company_code>', views.asset_assignment_view, name='asset_assignment_view'),
    path('asset-assignment-form/<str:batch_id>/', views.asset_assignment_form, name='asset_assignment_form'),
    path('assignments/<str:company_code>', views.assignments, name='assignments'),
    #
    path('companies/',views.companies,name="companies"),
    path('check_code/<int:code>/', views.check_code, name='check_code'),
    path('mail_config/<int:user_id>/<str:company_code>', views.email_update_config, name='email_update_config'),
    path('logout', views.logout_view, name='logout'),
    path("create-user/", views.create_user_view, name="create_user_view"),
    #
    # report
    # 
    path("user_based_asset/<str:company_code>", views.user_based_asset, name="user_based_asset"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)