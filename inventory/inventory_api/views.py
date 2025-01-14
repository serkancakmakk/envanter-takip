from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_track.mixins import get_company
from inventory_track.models import Brand, Category, Company, Model, Product, ProductStatus
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


class GetBrandsAPI(APIView):

    def get(self, request, company_code):
        # Kategori ID'sini al
        print('apiye geldi')
        category_id = request.GET.get('category_id')
        # Şirketi al (company_code'ye göre)
        company = get_object_or_404(Company, code=company_code)

        # Kategori ID'sinin sağlanıp sağlanmadığını kontrol et
        if not category_id:
            return Response({'error': 'Kategori ID\'si gereklidir.'}, status=400)

        # Kategorinin geçerli olup olmadığını kontrol et
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Geçerli bir kategori bulunamadı.'}, status=404)

        # Markaları kategori ve şirket bazında filtrele
        brands = Brand.objects.filter(category_id=category_id, company=company)

        # Eğer marka yoksa, hata mesajı dön
        if not brands.exists():
            return Response({'info': 'Belirtilen kategoride marka bulunamadı.'}, status=404)

        # Markaların verilerini al
        brands_data = [
            {'id': brand.id, 'category_name': brand.category.name, 'name': brand.name}
            for brand in brands
        ]
        
        return Response({'brands': brands_data})
class GetCategoriesAPI(APIView):

    def get(self, request, company_code):
    
        # Şirketi al (company_code'ye göre)
        company = get_object_or_404(Company, code=company_code)
        
        # Markaları kategori ve şirket bazında filtrele
        categories = Category.objects.filter(company=company,is_active=True)

        # Markaların verilerini al
        category_data = [
            {'id': category.id, 'category_name': category.name,}
            for category in categories
        ]
        print(category_data)
        return Response({'categories': category_data})

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
from .serializers import CompanySerializer, ProductSerializer     
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
class GetProductsAPI(APIView):
    def get(self, request, company_code):
        company = get_company(company_code)
        query = request.GET.get('q', '')  # Arama terimi
        page = int(request.GET.get('page', 1))  # Sayfa numarası
        page_size = 10  # Her sayfada gösterilecek ürün sayısı

        # Arama filtresi: Ürün adı veya kategori adı
        products = Product.objects.filter(
            company=company,
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
                'name': f"{product.category.name} - {product.brand.name} - {product.model.name}",
                'serial_number': product.serial_number
            }
            
            for product in products
                
        ]
        
        return Response({
            'results': products_data,
            'has_next': end < total_count  # Daha fazla sayfa olup olmadığını belirtir
        }, status=status.HTTP_200_OK)