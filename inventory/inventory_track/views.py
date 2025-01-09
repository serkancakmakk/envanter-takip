
import imaplib
import os
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

from .backends import LDAPBackend
from .services import authenticate_custom_user, authenticate_user
from .models import AssetAssignment, Brand, Category, CustomUser, UserMail, LdapConfig, LdapUser, Company, Model, Product, ProductStatus
from .models import Company, LdapUser,LdapGroup  # LdapUser modelinizi doğru şekilde içe aktarın
from ldap3 import Server, Connection, ALL, NTLM
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import get_all_ldap_users_and_groups
from .forms import BrandForm, CategoryForm, CompanyCreateForm, EmailUpdateForm, ModelForm
# For Company <---
from django.contrib.auth.decorators import login_required
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LdapConfig
from .forms import LdapConfigForm
from django.contrib.auth import authenticate,login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LdapConfig, Company
from .forms import LdapConfigForm
from django.shortcuts import render
from django.db.models import Count
from .models import Company, LdapUser
""" Master alanları """
def master_dashboard(request,company_code):
    # Tüm şirketleri almak
    company = get_object_or_404(Company,code = company_code)
    companies = Company.objects.all()
    print(companies)
    # Her şirket için, o şirkete ait kullanıcıları getirme
    company_users = {}
    for company in companies:
        # Bu şirketin kullanıcılarını alıyoruz
        users = LdapUser.objects.filter(company=company)
        company_users[company] = users

    return render(request, 'master_dashboard.html', {
        'company_users': company_users,
        'company':company,
    })
""" ŞİRKET OLUŞTURMA GÜNCELLEME VE DİĞERLERİ """
from .decorators import check_company_code
@check_company_code
def create_company(request):
    """
    Şirket oluşturmak için kullanılır
"""
    if request.method == 'POST':
        form = CompanyCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Şirket başarıyla oluşturuldu.")
            return redirect('create_company')  # Şirketler listesine yönlendirme
        else:
            # Formda hatalar varsa hata mesajlarını göstermek için
            print(form.errors)
            messages.error(request, "Formda hatalar var. Lütfen aşağıdaki hataları kontrol edin.")
    else:
        form = CompanyCreateForm()

    return render(request, 'create_company.html', {'form': form})
def edit_ldap_config(request, company_code):
    try:
        # Şirketi al
        company = Company.objects.get(code=company_code)

        # Şirketin LDAP ayarlarını al (veya oluştur)
        ldap_config, created = LdapConfig.objects.get_or_create(company=company)

        if request.method == 'POST':
            form = LdapConfigForm(request.POST, instance=ldap_config)
            if form.is_valid():
                # Boş alanları korumak için mevcut değeri al
                if not form.cleaned_data.get('base_dn'):
                    form.cleaned_data['base_dn'] = ldap_config.base_dn
                if not form.cleaned_data.get('bind_username'):
                    form.cleaned_data['bind_username'] = ldap_config.bind_username
                if not form.cleaned_data.get('bind_password'):
                    form.cleaned_data['bind_password'] = ldap_config.bind_password
                
                # Formu kaydet
                form.save()
                if created:
                    messages.success(request, 'Yeni LDAP ayarları başarıyla oluşturuldu.')
                else:
                    messages.success(request, 'LDAP ayarları başarıyla güncellendi.')
                print('BAŞARILI')
            else:
                messages.error(request, 'LDAP ayarlarında bir hata oluştu.')
                print(form.errors)

        else:
            form = LdapConfigForm(instance=ldap_config)

        return redirect('company_dashboard', company_code=company.code)  # Yönlendirme burada yapılacak

    except Company.DoesNotExist:
        messages.error(request, 'Şirket bulunamadı.')
        return redirect('company_dashboard', company_code=company_code)  # Yönlendirme burada yapılacak
from .mixins import check_company_permission    
def company_dashboard(request, company_code):
    # Şirketi veritabanından çek
    company = get_object_or_404(Company, code=company_code)
    try:
        ldap_configs = LdapConfig.objects.get(company=company)
    except LdapConfig.DoesNotExist:
        ldap_configs = None  # LDAP yapılandırması bulunamazsa None yap
    print(ldap_configs)
    # Eğer admin yetkisine sahipse, 'Kullanıcıları Çek' işlemi yapılabilir
    if request.method == "POST":
            print('Ldaptan kullanıcıları alıyor.')
            # LDAP'dan kullanıcıları al
            ldap_users = get_all_ldap_users_and_groups(company)
            print('Ldap kullanıcıları',ldap_users)
            # Kullanıcıları senkronize et
            # result = get_all_ldap_users_and_groups(ldap_users, company)
            print(ldap_users)
            
            # messages.success(request,result)
            return redirect('company_dashboard',company_code)

    # Template için şirket bilgilerini gönder
    context = {
        'ldap_configs':ldap_configs,
        'company': company
    }
    return render(request, 'company_dashboard.html',context)
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)
@check_company_permission
def create_custom_user_from_settings(request):
    # Kullanıcı adı ve şifreyi settings.py'den al
    username = getattr(settings, 'MASTER_USERNAME', None)
    password = getattr(settings, 'MASTER_PASSWORD', None)
    print(username)
    print(password)
    # Kullanıcı adı veya şifre eksikse işlem yapma
     # Kullanıcı adı veya şifre eksikse işlem yapma
    if not username or not password:
        messages.error(request, 'Kullanıcı adı veya şifre ayarlanmamış.')
        return HttpResponse("Eksik bilgi, kullanıcı oluşturulamadı.", status=400)

    # CustomUser modelini kullan
    User = get_user_model()

    # Kullanıcıyı oluştur
    try:
        user = User.objects.create_user(username=username, password=password,email="s@mail.com",company_code=1)
        user.save()
        messages.success(request, f"{username} başarıyla oluşturuldu!")
        return HttpResponse(f"Kullanıcı {username} başarıyla oluşturuldu!")
    except Exception as e:
        logger.error(f"Kullanıcı oluşturulurken bir hata oluştu: {str(e)}")
        messages.error(request, f"Kullanıcı oluşturulurken bir hata oluştu: {str(e)}")
        return HttpResponse(f"Bir hata oluştu: {str(e)}", status=500)
def master_login(request):
    """Master kullanıcı girişi için view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Master kullanıcıyı kontrol et
        if username == settings.MASTER_USERNAME and password == settings.MASTER_PASSWORD:
            # Master kullanıcı doğrulandı
            master_user, created = CustomUser.objects.get_or_create(username=username)
            authenticate ()
            login(request, master_user, backend='inventory_track.backend.CustomUserBackend')
            return redirect('master_dashboard')  # Master kullanıcıya özel panel
        else:
            messages.error(request, "Geçersiz Master kullanıcı bilgileri.")
            return redirect('master_login')  # Master login sayfasına geri yönlendir

    return render(request, 'master_login.html')

load_dotenv()

def master_login(request):
    if request.method == "POST":
        company_code = request.POST.get("company_code")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kullanıcıyı doğrula
        user, user_type = authenticate_custom_user(request, company_code, username, password)
        
        if user:
            # Başarılı giriş durumunda, kullanıcıyı giriş yap
            login(request, user, backend="inventory_track.backends.CustomUserBackend")
            print(request.user.username)
            # CustomUser dashboard'a yönlendir
            return redirect('product_page',request.user.company_code)  # CustomUser dashboard
        else:
            messages.error(request, "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.")
            return redirect('custom_login')  # Giriş sayfasına geri yönlendir
    
    return render(request, 'login.html')
def ldap_login_view(request):
    if request.method == 'POST':
        company_code = request.POST.get('company_code')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user, status_code = authenticate_user(request, company_code, username, password)
        print(status_code)
        if status_code == 'authenticated':
            login(request, user, backend="inventory_track.backends.LDAPBackend")
            messages.success(request, "Başarıyla giriş yaptınız.")
            return redirect('company_dashboard',company_code)
        elif status_code == 'invalid_company':
            messages.error(request, "Geçersiz şirket kodu.")
        elif status_code == 'no_ldap_config':
            messages.error(request, "Şirkete bağlı LDAP yapılandırması bulunamadı.")
        elif status_code == 'invalid_credentials':
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")
        elif status_code == 'ldap_connection_error':
            messages.error(request, "LDAP sunucusuna bağlanılamadı. Lütfen sistem yöneticinize başvurun.")
        else:
            messages.error(request, "Bilinmeyen bir hata oluştu.")

        return redirect('ldap_login')  # Hata durumunda giriş sayfasına geri dön

    return render(request, 'ldap_login.html')
""" ŞİRKET AYARLAMALARI SONU  """
from django.shortcuts import render
from django.db.models import Count
from .models import Company, Product

from django.db.models import Count
def get_products(company_code):
    # Belirtilen şirket koduna göre ürünleri filtrele
    try:
        company = Company.objects.get(code=company_code)
        products = Product.objects.filter(company=company)
        return products
    except Company.DoesNotExist:
        # Eğer şirket bulunamazsa boş bir QuerySet döndür
        return Product.objects.none()

def inventory(request, company_code):
    # Eğer kullanıcı master kullanıcı ise tüm firmalara erişebilir
    if request.user.company.code == settings.MASTER_COMPANY: # Master kullanıcı adı kontrolü
        try:
            company = Company.objects.get(code=company_code)
        except Company.DoesNotExist:
            messages.error(request, "Geçersiz şirket kodu. Lütfen tekrar kontrol edin.")
            return redirect('inventory', company_code=request.user.company.code)
    else:
        # Eğer normal kullanıcı ise sadece kendi firmasına yönlendirilir
        if request.user.company.code != company_code:
            messages.error(request, "Kendi firmanıza yönlendirdiniz.")
            return redirect('inventory', company_code=request.user.company.code)
        
        try:
            company = Company.objects.get(code=company_code)
        except Company.DoesNotExist:
            messages.error(request, "Geçersiz şirket kodu. Lütfen tekrar kontrol edin.")
            return redirect(request.META.get('HTTP_REFERER'))

    # Ürünleri getir
    products = get_products(company_code)

    context = {
        'company': company,
        'products': products,
    }

    return render(request, 'inventory.html', context)



from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import CategoryForm, BrandForm, ModelForm,ProductStatusForm

# Create Product View
from django.http import JsonResponse
def check_company_code(request, company_code):
    """
    Kullanıcının şirket kodunu kontrol eder.
    Eşleşmiyorsa bir yönlendirme ya da hata yanıtı döndürür.
    """
    if request.user.company.code != company_code:
        messages.info(request, 'Sadece kendi şirketinizde işlem yapabilirsiniz.')
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Referer yoksa anasayfaya yönlendir
    return None  # Kontrol geçildi, hata yok.
from common.decorators import company_required

# @company_required
def product_page(request, company_code):
# Şirket ve ürün bilgilerini al
    # company = get_company(company_code)
    company=get_object_or_404(Company,code=company_code)
    products = Product.objects.filter(company=company)
    categories = Category.objects.filter(company=company)
    brands = Brand.objects.filter(company=company)
    models = Model.objects.filter(company=company)
    statuses = ProductStatus.objects.filter(company=company)

    # Verileri şablona gönder
    context = {
        'statuses': statuses,
        'models': models,
        'brands': brands,
        'categories': categories,
        'company': company,
        'products': products,
    }
    return render(request, 'add_product.html', context)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Company, Product, Category, Brand, Model
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Eğer CSRF hatası varsa, bu dekoratör geçici olarak eklenebilir

def create_product(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    print('product ekleme viewsina geldi')
    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        model_id = request.POST.get('model')
        serial_number = request.POST.get('serial_number')
        status = request.POST.get('status')
        product_status = get_object_or_404(ProductStatus,id=status)
        print(product_status.id)
        # Aynı seri numarasından ürün var mı kontrol et
        if Product.objects.filter(serial_number=serial_number, company=company).exists():
            return JsonResponse({'success': False, 'error': f"Bu '{serial_number}' seri numaralı ürün zaten kayıtlı."})

        # Get the instances
        try:
            category = Category.objects.get(id=category_id)
            brand = Brand.objects.get(id=brand_id)
            model = Model.objects.get(id=model_id)

            # Create the product
            product = Product.objects.create(
                category=category,
                brand=brand,
                model=model,
                serial_number=serial_number,
                company=company,
                created_by=request.user,
                status = product_status,
            )

            # Return JSON response with the new product data
            return JsonResponse({
                'success': True,
                'product': {
                    'id': product.id,
                    'category': product.category.name,
                    'brand': product.brand.name,
                    'model': product.model.name,
                    'serial_number': product.serial_number,
                    'status': product.status.name,
                    'date_joined': product.date_joined,
                    'created_by': f"{product.created_by.first_name} {product.created_by.last_name}"
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from datetime import date       
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, LdapUser, AssetAssignment, Category, Company

from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, LdapUser, AssetAssignment, Category, Company

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from datetime import date
from .models import Product, LdapUser, AssetAssignment, Category, Company
from datetime import datetime
from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Company, LdapUser, Product, AssetAssignment
from datetime import date
import uuid
def asset_assignment_form(request, batch_id):
    # Batch ID'ye göre AssetAssignment kayıtlarını filtrele
    assignments = AssetAssignment.objects.filter(batch_id=batch_id)
    
    # Eğer batch_id ile ilgili bir kayıt bulunamazsa 404 hata döndür
    if not assignments:
        raise Http404("Zimmet formu bulunamadı.")
    
    # İlgili şirket bilgisi, ürünler ve kullanıcılar
    company = assignments.first().company  # Bütün ürünler aynı şirkete ait olacak
    products = [assignment.product for assignment in assignments]
    employees = LdapUser.objects.filter(company=company)
    
    context = {
        'assignments': assignments,
        'company': company,
        'products': products,
        'employees': employees,
        'batch_id': batch_id,
    }

    # asset_assignment_form.html şablonunu render et
    return render(request, 'asset_assignment_form.html', context)
from django.template.loader import render_to_string
# from weasyprint import HTML
from itertools import groupby
from operator import attrgetter
def assignments(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    all_assignments = AssetAssignment.objects.filter(company=company).select_related('assign_by', 'assign_to', 'product')
    
    # Batch ID'ye göre gruplama
    assignments = {
        batch_id: list(items)
        for batch_id, items in groupby(all_assignments, key=attrgetter('batch_id'))
    }
    
    context = {
        'company': company,
        'assignments': assignments,
    }
    return render(request, 'assignments.html', context)
from django.http import HttpResponse
def assignments(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    assignments = AssetAssignment.objects.filter(company=company).order_by('batch_id')
    
    # Gruplama işlemi
    grouped_assignments = {
        key: list(group) for key, group in groupby(assignments, key=attrgetter('batch_id'))
    }

    context = {
        'company': company,
        'assignments': grouped_assignments,  # Şablona gruplanmış veri gönder
    }
    return render(request, 'assignments.html', context)
def asset_assignment_view(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    employees = LdapUser.objects.filter(company=company)
    categories = Category.objects.filter(company=company)

    today = date.today()
    products = Product.objects.filter(company=company, assign_to__isnull=True)

    if request.method == 'POST':
        selected_products = request.POST.get('selected_product_ids')
        if selected_products:
            selected_products = selected_products.split(',')  # Virgülle ayrılmış id'leri listeye çevir

        assign_to = request.POST.get('assign_to')
        info = request.POST.get('info')
        assign_date = request.POST.get('assign_date')
        return_date = request.POST.get('return_date')
        appointed_company = request.POST.get('appointed_company')
        appointed_address = request.POST.get('appointed_address')
        # Handle empty or invalid date inputs
        try:
            if assign_date:
                if len(assign_date) > 10:  # Assuming it includes time
                    assign_date = datetime.strptime(assign_date, '%Y-%m-%d %H:%M')
                else:
                    assign_date = datetime.strptime(assign_date, '%Y-%m-%d')

            if return_date:
                if len(return_date) > 10:  # Assuming it includes time
                    return_date = datetime.strptime(return_date, '%Y-%m-%d %H:%M')
                elif return_date != '':  # Only parse if it's provided
                    return_date = datetime.strptime(return_date, '%Y-%m-%d')
                else:
                    return_date = None  # If no return date is provided, set it as None
        except ValueError:
            messages.error(request, "Geçersiz tarih formatı.")
            return redirect('asset_assignment_view', company_code=company_code)

        # Proceed if no missing required fields
        if not selected_products or not assign_to:
            messages.error(request, "Lütfen ürünleri ve bir kullanıcı seçin.")
            return redirect('asset_assignment_view', company_code=company_code)

        recipient = get_object_or_404(LdapUser, id=assign_to)

        # Batch ID'yi oluştur
        batch_user = get_object_or_404(LdapUser,id=assign_to)
        batch_id = f"{batch_user.first_name}_{batch_user.last_name}_{assign_date}_{uuid.uuid4()}"
        if request.user.company.code != recipient.company.code:
            print(recipient.company.code)
            messages.error(request, "Hatalı işlem yapıldı lütfen kendi şirketinizden birini seçin")
            return redirect('asset_assignment_view', company_code=company_code)
        # Seçilen ürünleri zimmetle
        for product_id in selected_products:
            product = get_object_or_404(Product, id=product_id, company=company)

            # AssetAssignment kaydını oluştur ve batch_id'yi ata
            asset_assignment = AssetAssignment.objects.create(
                company = company,
                product=product,
                assign_by=request.user,
                assign_to=recipient,
                info=info,
                assign_date=assign_date,
                return_status=None,
                appointed_company = appointed_company,
                appointed_address = appointed_address,
                batch_id=batch_id,  # Aynı grupta olan ürünler için aynı batch_id
                is_active=True,
            )
            asset_assignment.save()
        messages.success(request, "Ürünler başarıyla zimmetlendi.")
        return redirect('asset_assignment_view', company_code=company_code)

    return render(request, 'asset_assignment.html', {
        'today': today,
        'products': products,
        'company': company,
        'employees': employees,
        'categories': categories,
    })

def add_category(request, company_code):
    """
    Kategori Eklemek için
    """
    company = get_object_or_404(Company, code=company_code)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        category_name = request.POST.get('name')
        
        # Trim the category name to remove any extra spaces
        category_name = category_name.strip() if category_name else ""
        
        if category_name:
            # Check if a category with the same name already exists for the given company
            if Category.objects.filter(name=category_name, company=company).exists():
                return JsonResponse({'success': False, 'message': 'Bu kategori adı zaten mevcut!'})
            
            # Create and save the new category
            new_category = Category(name=category_name, company=company, created_by=request.user)
            new_category.save()
            
            return JsonResponse({'success': True, 'message': 'Kategori başarıyla eklendi!'})
        else:
            return JsonResponse({'success': False, 'message': 'Kategori adı boş olamaz!'})
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)


def add_brand_view(request,company_code):
    """
    Marka Eklemek için
    """
    print('Add branda geldi')
    company = get_object_or_404(Company,code = company_code)
    if request.method == 'POST':
        form = BrandForm(request.POST, company=company)
        if form.is_valid():
            brand = form.save(commit=False)
            brand.company = company
            brand.created_by = request.user
            brand.save()
            return JsonResponse({'success': True, 'message': 'Marka başarıyla eklendi!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def add_model_view(request, company_code):
    company = get_company(company_code)
    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.company = company
            model.created_by = request.user
            model.save()
            return JsonResponse({'success': True, 'message': 'Model başarıyla eklendi!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
from .mixins import get_company  # doğru import

def add_product_status_view(request,company_code):
    if request.method == 'POST':
        print('viewsa geldi')
        # company = get_company(company_code)
        company = get_object_or_404(Company,code=company_code)
        form = ProductStatusForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.company = company
            model.created_by = request.user
            model.save()
            return JsonResponse({'success': True, 'message': 'Model başarıyla eklendi!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def manage_entities_view(request,company_code):
    company = get_company(company_code)
    category_form = CategoryForm(company=company)
    brand_form = BrandForm(company=company)
    product_status_form = ProductStatusForm()
    model_form = ModelForm(company=company)
    brands = Brand.objects.filter(company=request.user.company)
    return render(request, 'manage_entities.html', {
        'brands':brands,
        'product_status_form':product_status_form,
        'category_form': category_form,
        'brand_form': brand_form,
        'model_form': model_form,
        'company':company,
    })

from django.http import JsonResponse
from .models import Category, Brand, Model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Brand, Model

@login_required
def get_categories(request,company_code):
    company =  get_object_or_404(Company,code = company_code)
    print('Buraya geldi category')
    categories = Category.objects.filter(company=company).values('id', 'name')
    print("Categories:", categories)
    return JsonResponse({'categories': list(categories)})
# @login_required
# def get_product_statuses(request,company_code):
#     company =  get_object_or_404(Company,code = company_code)
#     statuses = ProductStatus.objects.filter(company=company)  # Şirkete göre filtreleme yapıyoruz
#     status_data = [{"id": status.id, "name": status.name} for status in statuses]
#     return JsonResponse(status_data, safe=False)

    
@login_required
def get_brands(request,company_code):
    category_id = request.GET.get('category_id')
    print(category_id)
    company =  get_object_or_404(Company,code = company_code)

    if not category_id:
        return JsonResponse({'error': 'Kategori ID\'si gereklidir.'}, status=400)

    # Markaları kategori bazında filtrele
    brands = Brand.objects.filter(category_id=category_id, company=company)
    brands_data = [{'id': brand.id, 'category_name': brand.category.name,'name': brand.name} for brand in brands]

    return JsonResponse({'brands': brands_data})
# Modelleri markaya göre getir
@login_required
def get_models(request,company_code):
    company =  get_object_or_404(Company,code = company_code)
    brand_id = request.GET.get('brand_id')
    models = Model.objects.filter(company=company,brand_id=brand_id).select_related('brand__category').values(
        'id', 'name', 'brand__name', 'brand__category__name'
    )
    print(models)
    return JsonResponse({'models': list(models)})
from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('company_login')
# # # # # # 
import imaplib
import email
from email.header import decode_header



def get_user_emails(request):
    # get_emails fonksiyonuna request parametresi gönder
    emails = get_emails(request)  # artık request'i gönderiyoruz
    
    for email in emails:
        # E-postaları veritabanına kaydet
        UserMail.objects.create(
            user=request.user,  # Bu e-posta kimliği kullanıcıya ait
            subject=email['subject'],
            sender=email['from'],
            body=email['body'],
            company=request.user.company,  # Kullanıcının şirketini atayın
            relating=request.user  # Bağlı olduğu kullanıcıyı atayın
        )
    
    return HttpResponse("E-postalar başarıyla çekildi ve kaydedildi.")

def email_update_config(request, user_id,company_code):
    # Kullanıcıyı al
    ldap_user = get_object_or_404(LdapUser, id=user_id)
    company = get_object_or_404(Company,code=company_code)
    if request.method == 'POST':
        # Formu doldur ve doğrula
        form = EmailUpdateForm(request.POST, instance=ldap_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-posta adresi ve şifresi başarıyla güncellendi.')
            return redirect('email_update_config', user_id=user_id)  # Güncel sayfaya yeniden yönlendirme
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        # GET isteği için formu önceden doldur
        form = EmailUpdateForm(instance=ldap_user)

    return render(request, 'email_update_form.html', {'form': form, 'ldap_user': ldap_user,'company':company,})
def companies(request):
    if request.user.company.code != settings.MASTER_COMPANY:
        messages.error(request, "Lütfen ürünleri ve bir kullanıcı seçin.")
        return redirect('company_dashboard', request.user.company.code)
    add_company_form = CompanyCreateForm()
    companies = Company.objects.all()  # Tüm şirketleri getir
    context = {
        'add_company_form':add_company_form,
        'companies': companies,
    }
    return render(request, 'companies.html', context)
def check_code(request, code):
    # Veritabanında aynı koda sahip bir şirket var mı diye kontrol et
    exists = Company.objects.filter(code=code).exists()
    
    # JSON olarak yanıt döndür
    return JsonResponse({'exists': exists})