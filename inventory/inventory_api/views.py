from venv import logger
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_track.mixins import get_company
from inventory_track.models import AssetAssignment, Brand, Category, Company, LdapUser, Model, Product, ProductStatus
from rest_framework.exceptions import NotFound
# Create your views here.
from rest_framework.permissions import IsAuthenticated
class GetModelsAPI(APIView):
    def get(self, request, company_code):
        try:
            brand_id = request.GET.get('brand_id')
            company = get_object_or_404(Company, code=company_code)
            print('Get models apiye geldi')
            if not brand_id:
                return Response({'error': 'Marka ID\'si gereklidir.'}, status=400)
            
            brand = get_object_or_404(Brand, id=brand_id, company=company)

            models = Model.objects.filter(brand=brand, brand__company=company)
            
            if not models.exists():
                return Response({'info': 'Belirtilen marka için model bulunamadı.'}, status=404)

            models_data = [
                {'id': model.id, 'name': model.name, 'brand_name': model.brand.name, 'category_name': model.brand.category.name}
                for model in models
            ]
            print('Models_DAta',models_data)
            return Response({'models': models_data})
        except Exception as e:
            print(f"Error: {str(e)}")  # Hata mesajını konsola yazdır
            return Response({'error': 'Sunucu hatası. Lütfen tekrar deneyin.'}, status=500)

from rest_framework.pagination import PageNumberPagination
class GetBrandsAPI(APIView):
    
    def get(self, request, company_code):
        # Şirketi al
        company = get_object_or_404(Company, code=company_code)
        print(company)
        # Markaları filtrele
        category_id = request.GET.get('category_id')
        if category_id:
            category = get_object_or_404(Category, id=category_id, company=company)
            print(category)
            brands = Brand.objects.filter(category=category, company=company).order_by('id')
            print(brands)
        else:
            brands = Brand.objects.filter(company=company, is_active=True).order_by('id')
            print(brands)
        print(brands)
        # Eğer `all=true` parametresi varsa, tüm markaları döndür
        print(request.GET.get)
        if request.GET.get('all'):
            brand_data = [
                {'id': brand.id, 'name': brand.name, 'category_name': brand.category.name if brand.category else 'Bilinmeyen'}
                for brand in brands
            ]
            return Response({'brands': brand_data})

        # Sayfalama işlemi
        page_number = request.GET.get('page', 1)
        paginator = Paginator(brands, 5)  # Sayfa başına 5 marka
        page_obj = paginator.get_page(page_number)

        brand_data = [
            {'id': brand.id, 'name': brand.name, 'category_name': brand.category.name if brand.category else 'Bilinmeyen'}
            for brand in page_obj
        ]
        print(brand_data)
        return Response({
            'brands': brand_data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })

from django.core.paginator import Paginator
class GetCategoriesAPI(APIView):

    def get(self, request, company_code):
        company = get_object_or_404(Company, code=company_code)
        categories = Category.objects.filter(company=company).order_by('-id')

        if request.GET.get('all'):
            logger.info('all a geldi')  # `print` yerine `logger`
            category_data = [
                {'id': category.id, 'category_name': category.name}
                for category in categories
            ]
            return Response({'categories': category_data})

        page_number = request.GET.get('page', 1)
        paginator = Paginator(categories, 5)
        page_obj = paginator.get_page(page_number)

        category_data = [
            {'id': category.id, 'category_name': category.name}
            for category in page_obj
        ]

        return Response({
            'categories': category_data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })

from django.http import JsonResponse
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings


from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DeleteCategoryAPI(APIView):
    
    def delete(self, request, category_id, *args, **kwargs):
        try:
            # Kullanıcının şirket kodunu kontrol et
            if request.user.company is None:
                print('Kullanıcı şirketi atanmış değil')
                return Response({'error': 'Kullanıcının şirketi atanmış değil.'}, status=status.HTTP_400_BAD_REQUEST)

            # Kategoriyi al
            category = Category.objects.get(id=category_id)
            
            # Kullanıcı ve kategori şirket kodlarını kontrol et
            print(f"Kullanıcı şirket kodu: {request.user.company.code}")
            print(f"Kategori şirket kodu: {category.company.code}")
            
            # Kullanıcı ve kategori şirket kodlarının eşleşip eşleşmediğini kontrol et
            if request.user.company.code != category.company.code:
                return Response({'error': 'Bu kategoriye erişim izniniz yok.'}, status=status.HTTP_403_FORBIDDEN)

            # Erişim izni varsa, kategoriyi pasifleştir
            category.is_active = False
            category.save()
            return Response({'message': 'Kategori silindi!'}, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response({'error': 'Kategori bulunamadı!'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({'error': f'Bir hata oluştu: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetStatusAPI(APIView):
    def get(self, request, company_code):
        # Şirketi al
        company = get_object_or_404(Company, code=company_code)
        
        # Şirkete ait tüm durumu al
        statuses = ProductStatus.objects.filter(company=company)

        # Durumların verilerini hazırlayıp JSON formatında döndür
        statuses_data = [
            {'id': status.id, 'name': status.name}  # 'status' nesnesinin her birini kullan
            for status in statuses
        ]
        print(statuses_data)
        return Response({'statuses': statuses_data}, status=status.HTTP_200_OK)
class CreateStatusAPIView(APIView):
    def post(self, request, company_code):
        # Şirket doğrulama
        company = get_company(company_code)
        if not company:
            return Response({"error": "Şirket bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        # Gelen verilerden yeni durum oluştur
        status_name = request.data.get("name")
        if not status_name:
            return Response({"error": "Durum adı gerekli."}, status=status.HTTP_400_BAD_REQUEST)

        # Durum oluştur
        new_status = ProductStatus.objects.create(name=status_name, company=company)
        return Response({"message": "Durum başarıyla oluşturuldu.", "id": new_status.id}, status=status.HTTP_201_CREATED)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from inventory_track.models import Company
from .serializers import AssetAssignmentSerializer, CompanySerializer, ProductSerializer     
class CompanyListView(APIView):
    def get(self, request,company_code):
        search_term = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)
        print('Company list apiye geldi')
        # Arama filtresi
        companies = Company.objects.filter(name__icontains=search_term)

        # Sayfalama
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(companies, request)

        # Şirket verilerini hazırlama
        serializer = CompanySerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
import logging
logger = logging.getLogger(__name__)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from .serializers import AssetAssignmentSerializer
import logging

logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

class ReportAssetAssignmentView(APIView):
    def get(self, request, company_id, user_id):
        # Kullanıcı modellerini al
        UserModel = get_user_model()  # Django'nun User modeli
        ldap_user_model = LdapUser  # Özel LDAP kullanıcı modeli
        
        # Önce User tablosunda ara
        user = UserModel.objects.filter(id=user_id).first()
        
        # Eğer User tablosunda yoksa LdapUser tablosunda ara
        if not user:
            user = ldap_user_model.objects.filter(id=user_id).first()
        
        # Kullanıcı bulunamazsa hata döndür
        if not user:
            return Response(
                {"detail": _("Belirtilen kullanıcı bulunamadı.")},
                status=status.HTTP_404_NOT_FOUND
            )

        logger.debug(_("User: %(username)s") % {'username': user.username})

        # Yetkilendirme kontrolü: Master company veya aynı şirket
        if not (
            request.user.company.code == settings.MASTER_COMPANY or
            request.user.company.id == user.company.id
        ):
            return Response(
                {"detail": _("Bu verilere erişim izniniz yok.")},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kullanıcının atamalarını almak için ContentType belirle
        user_content_type_id = ContentType.objects.get_for_model(user).id
        print(user.id)
        print(user_content_type_id)
        print(company_id)
        # Kullanıcıya atanmış varlıkları getir
        assignments = AssetAssignment.objects.filter(
            assign_to_content_type_id=user_content_type_id,
            assign_to_object_id=user.id,
            company_id=company_id
        )
        print('assignment',assignments)
        logger.debug(_("Assignments: %(assignments)s") % {'assignments': assignments})

        if not assignments.exists():
            return Response(
                {"detail": _("Kullanıcı (%(username)s) için atanmış bir varlık bulunamadı.") % {'username': user.username}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verileri serialize et
        serialized_data = AssetAssignmentSerializer(assignments, many=True)

        return Response(serialized_data.data, status=status.HTTP_200_OK)



class GetProductsAPI(APIView):
    def get(self, request, company_code):
        company = get_company(company_code)
        query = request.GET.get('q', '')  # Arama terimi
        page = int(request.GET.get('page', 1))  # Sayfa numarası
        page_size = 10  # Her sayfada gösterilecek ürün sayısı

        # Arama filtresi: Ürün adı veya kategori adı
        products = Product.objects.filter(
            company=company,
            assign_by_content_type__isnull=True,
            assign_to_content_type__isnull=True,
            serial_number__icontains=query  # Kategori adına göre filtreleme
        )
        total_count = products.count()  # Toplam ürün sayısı

        # Sayfalama
        start = (page - 1) * page_size
        end = start + page_size
        products = products[start:end]

        # Ürün bilgilerini hazırlama
        products_data = [
            {
                'id': product.id,
                'category': {product.category.name},
                'brand': {product.brand.name},
                'model':{product.model.name},
                'serial_number': product.serial_number,
                'status': product.status.name,
            }
            
            for product in products
                
        ]
        
        return Response({
            'results': products_data,
            'has_next': end < total_count  # Daha fazla sayfa olup olmadığını belirtir
        }, status=status.HTTP_200_OK)
class GetProductsStatusAPI(APIView):
    def get(self, request, company_code):
        company = get_company(company_code)
        statutes = ProductStatus.objects.filter(
            company=company,
              # Kategori adına göre filtreleme
        )
        
        statutes_data = [
            {
                'name': statutes.name,
                
            }
            
            for status in statutes
                
        ]
        
        return Response({
            'statutes': statutes,
        }, status=status.HTTP_200_OK)