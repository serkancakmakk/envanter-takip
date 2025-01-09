

from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateStatusAPIView, DeleteCategoryAPI, GetBrandsAPI, GetCategoriesAPI,  GetModelsAPI, GetStatusAPI
urlpatterns = [
    path('get_models_api/<str:company_code>/', GetModelsAPI.as_view(), name='get_models_api'),
    path('get_brands_api/<str:company_code>/', GetBrandsAPI.as_view(), name='get_brands_api'),
    path("create_status_api/<str:company_code>/", CreateStatusAPIView.as_view(), name="create_status_api"),
    path("get_statutes_api/<str:company_code>/", GetStatusAPI.as_view(), name='get_statutes_api'),
    path('get_categories_api/<str:company_code>/', GetCategoriesAPI.as_view(), name='get_categories_api'),
    path('companies/', views.CompanyListView.as_view(), name='company_list_api'),
    path('get_products_api/<str:company_code>/', views.GetProductsAPI.as_view(), name='get_products_api'),
    path('delete_category_api/<int:category_id>/', DeleteCategoryAPI.as_view(), name='delete_category_api'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)