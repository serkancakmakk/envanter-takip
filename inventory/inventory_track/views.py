
import imaplib
import json
import os
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

from .backends import LDAPBackend
from .services import authenticate_custom_user, authenticate_user
from .models import AssetAssignment, Brand, Category, CustomUser,  LdapConfig, LdapUser, Company, Model, Product, ProductStatus
from .models import Company, LdapUser  # LdapUser modelinizi doğru şekilde içe aktarın
from ldap3 import Server, Connection, ALL, NTLM
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import get_all_ldap_users_and_groups
from .forms import BrandForm, CategoryForm, CompanyCreateForm, CustomUserEditForm, EmailUpdateForm, ModelForm
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
# @check_company_code
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
                    form.cleaned_data['bind_password'] = ldap_config.bind_password_encrypted
                
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
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import Company
""" Kullanıcı Ekleme Ve Düzenleme İşlemleri """
def edit_user(request, user_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = get_object_or_404(CustomUser, id=user_id)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        user.is_active = data.get('is_active', user.is_active)
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def list_users(request, company_code):
    # Kullanıcının şirket kodunu kontrol et
    company = get_company(company_code)
    if request.user.company.code == settings.MASTER_COMPANY:
        # MASTER_COMPANY için LdapUser tablosundaki kullanıcıları al
        users = CustomUser.objects.values(
            'id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'phone'
        )
    else:
        # Diğer kullanıcılar için CustomUser tablosundaki kullanıcıları al
        users = LdapUser.objects.values(
            'id', 'username', 'email', 'first_name', 'last_name', 'is_active'
        )
    
    # Bağlam verilerini oluştur
    context = {
        'company':company,
        'users': users,
    }
    return render(request, 'list_users.html', context)
@check_company_code
def create_user(request, company_code):
    user_company = get_object_or_404(Company,code=  settings.MASTER_COMPANY)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tag = 'Support'
            user.company = user_company  # Şirketi kullanıcıya ata
            user.company_code = user_company.code # Şirket kodunu kullanıcıya ata
            user.save()
            messages.success(request,'Kullanıcı Başarıyla Oluşturuldu.')
            return redirect('create_user',request.user.company.code)  # Başarılı işlem sonrası yönlendirme
    else:
        
        form = CustomUserCreationForm()
        print(form.errors)
    return render(request, 'admin_area/create_user.html', {'form': form})
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
# Kullanıcı doğrulama işlemlerini modülerleştirme
def authenticate_and_login(request, company_code, username, password, is_master_login=False):
    """
    Kullanıcıyı doğrular ve giriş yapar.
    
    Args:
        request: Django HTTP isteği.
        company_code: Şirket kodu.
        username: Kullanıcı adı.
        password: Kullanıcı şifresi.
        is_master_login: Master login mi olduğunu belirler.

    Returns:
        redirect: Başarılı girişte yönlendirme objesi.
        messages: Hatalı girişte hata mesajı.
    """
    if company_code == settings.MASTER_COMPANY:
        user, user_type = authenticate_custom_user(request, company_code, username, password)
        if not user:
            messages.error(request, "Kullanıcı bulunamadı")
            return redirect('master_login' if is_master_login else 'ldap_login')

        if not user.is_active:
            messages.error(request, "Kullanıcı aktif değil")
            return redirect('master_login' if is_master_login else 'ldap_login')

        # Başarılı giriş
        login(request, user, backend="inventory_track.backends.CustomUserBackend")
        return redirect('product_page', request.user.company_code)

    # LDAP kullanıcı doğrulama
    user, status_code = authenticate_user(request, company_code, username, password)

    ldap_error_messages = {
        'invalid_company': "Geçersiz şirket kodu.",
        'no_ldap_config': "Şirkete bağlı LDAP yapılandırması bulunamadı.",
        'invalid_credentials': "Kullanıcı adı veya şifre hatalı.",
        'ldap_connection_error': "LDAP sunucusuna bağlanılamadı. Lütfen sistem yöneticinize başvurun."
    }

    if status_code == 'authenticated':
        login(request, user, backend="inventory_track.backends.LDAPBackend")
        messages.success(request, "Başarıyla giriş yaptınız.")
        return redirect('company_dashboard', company_code)
    elif status_code in ldap_error_messages:
        messages.error(request, ldap_error_messages[status_code])
    else:
        messages.error(request, "Bilinmeyen bir hata oluştu.")

    return redirect('ldap_login')

# Master login
def master_login(request):
    if request.method == "POST":
        company_code = request.POST.get("company_code")
        username = request.POST.get("username")
        password = request.POST.get("password")

        return authenticate_and_login(request, company_code, username, password, is_master_login=True)

    return render(request, 'login.html')

# LDAP login
def ldap_login_view(request):
    if request.method == 'POST':
        company_code = request.POST.get('company_code')
        username = request.POST.get('username')
        password = request.POST.get('password')

        return authenticate_and_login(request, company_code, username, password)

    context = {
        'SUPPORT_LOGIN_URL': settings.SUPPORT_LOGIN_URL,
    }
    return render(request, 'ldap_login.html', context)

""" ŞİRKET AYARLAMALARI SONU  """
from django.shortcuts import render
from django.db.models import Count
from .models import Company, Product

from django.db.models import Count

def inventory(request, company_code):
    # Eğer kullanıcı master kullanıcı ise tüm firmalara erişebilir
    if request.user.company.code == settings.MASTER_COMPANY:  # Master kullanıcı adı kontrolü
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

    context = {
        'company': company,
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
    print('product ekleme viewsine geldi')

    if request.method == 'POST':
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        model_id = request.POST.get('model')
        serial_number = request.POST.get('serial_number')
        status = request.POST.get('status')

        product_status = get_object_or_404(ProductStatus, id=status)
        print(f"Product status ID: {product_status.id}")

        # Aynı seri numarasından ürün var mı kontrol et
        if Product.objects.filter(serial_number=serial_number, company=company).exists():
            return JsonResponse({'success': False, 'error': f"Bu '{serial_number}' seri numaralı ürün zaten kayıtlı."})

        # Kullanıcı modeli ve ContentType belirleme
        user = request.user
        user_content_type = ContentType.objects.get_for_model(user.__class__)

        try:
            category = Category.objects.get(id=category_id)
            brand = Brand.objects.get(id=brand_id)
            model = Model.objects.get(id=model_id)

            # Ürünü oluştur
            product = Product.objects.create(
                category=category,
                brand=brand,
                model=model,
                serial_number=serial_number,
                company=company,
                created_by_content_type_id=user_content_type.id,  # User modelinin content type'ı
                created_by_object_id=user.id,  # Kullanıcının ID'si
                status=product_status,
            )

            # JSON yanıtı döndür
            return JsonResponse({
                'success': True,
                'product': {
                    'category': product.category.name,
                    'brand': product.brand.name,
                    'model': product.model.name,
                    'unit': product.model.unit,
                    'serial_number': product.serial_number,
                    'status': product.status.name,
                    'date_joined': product.date_joined,
                    'created_by': f"{user.first_name} {user.last_name}"
                }
            })

        except Exception as e:
            print(f"Error creating product: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Bir hata oluştu: {str(e)}"})

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
def undo_assignments(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    all_assignments = AssetAssignment.objects.filter(company=company).select_related('product')

    
    # Batch ID'ye göre gruplama
    assignments = {
        batch_id: list(items)
        for batch_id, items in groupby(all_assignments, key=attrgetter('batch_id'))
    }
    
    context = {
        'company': company,
        'assignments': assignments,
    }
    return render(request, 'undo_assignments.html', context)
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
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import Http404
from datetime import datetime
import uuid
from .models import Company, Product, LdapUser, CustomUser, Category, AssetAssignment
def undo_assignment_view(request,batch_id,company_code):
    company = get_company(company_code)
    if request.method == "POST":
        assignment = get_object_or_404(AssetAssignment,batch_id=batch_id,company=company)
        assignment.return_date = datetime.now()
        assignment.save()
        return redirect('success')
            
def asset_assignment_view(request, company_code):
    # Şirketi alıyoruz
    company = get_object_or_404(Company, code=company_code)
    
    # Kullanıcıları alıyoruz
    ldap_users = LdapUser.objects.filter(company=company)
    custom_users = CustomUser.objects.filter(company=company)
    
    # Ortak formatta kullanıcıları birleştiriyoruz
    employees = []
    for ldap_user in ldap_users:
        employees.append({
            'id': ldap_user.id,
            'name': ldap_user.first_name,
            'company': ldap_user.company,
            'email': ldap_user.email,
        })
    for custom_user in custom_users:
        employees.append({
            'id': custom_user.id,
            'name': custom_user.first_name,
            'company': custom_user.company,
            'email': custom_user.email,
        })
    
    # Kategorileri alıyoruz
    categories = Category.objects.filter(company=company)

    # Bugünün tarihini alıyoruz
    today = datetime.today().date()

    # Atanmamış ürünleri alıyoruz
    products = Product.objects.filter(
        company=company,
        assign_by_content_type__isnull=True,
        assign_to_content_type__isnull=True
    ).select_related('category', 'brand', 'model')

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

        # Tarihlerin doğru formatta olduğundan emin olalım
        try:
            if assign_date:
                if len(assign_date) > 10:  # Tarih saat içeriyorsa
                    assign_date = datetime.strptime(assign_date, '%Y-%m-%d %H:%M')
                else:
                    assign_date = datetime.strptime(assign_date, '%Y-%m-%d')

            if return_date:
                if len(return_date) > 10:  # Tarih saat içeriyorsa
                    return_date = datetime.strptime(return_date, '%Y-%m-%d %H:%M')
                elif return_date != '':  # Sadece verildiyse
                    return_date = datetime.strptime(return_date, '%Y-%m-%d')
                else:
                    return_date = None  # Geri iade tarihi yoksa None

        except ValueError:
            messages.error(request, "Geçersiz tarih formatı.")
            return redirect('asset_assignment_view', company_code=company_code)

        # Zimmetleme için gerekli alanların dolu olduğundan emin olalım
        if not selected_products or not assign_to:
            messages.error(request, "Lütfen ürünleri ve bir kullanıcı seçin.")
            return redirect('asset_assignment_view', company_code=company_code)

        # Kullanıcıyı almak için LdapUser veya CustomUser'ı kontrol edelim
        try:
            recipient = LdapUser.objects.get(id=assign_to, company=company)
            recipient_content_type = ContentType.objects.get_for_model(LdapUser)
        except LdapUser.DoesNotExist:
            try:
                recipient = CustomUser.objects.get(id=assign_to, company=company)
                recipient_content_type = ContentType.objects.get_for_model(CustomUser)
            except CustomUser.DoesNotExist:
                raise Http404("Kullanıcı bulunamadı.")

        # Batch ID'yi oluşturuyoruz
        batch_user = recipient  # 'recipient' doğru kullanıcıyı tutuyor
        batch_id = f"{batch_user.first_name}_{batch_user.last_name}_{assign_date}_{uuid.uuid4()}"

        # Şirket kontrolü
        if request.user.company.code != recipient.company.code:
            messages.error(request, "Hatalı işlem yapıldı lütfen kendi şirketinizden birini seçin")
            return redirect('asset_assignment_view', company_code=company_code)

        # Ürünleri zimmetliyoruz
        for product_id in selected_products:
            product = get_object_or_404(Product, id=product_id, company=company)
            print(product)
            product.assign_to_content_type = recipient_content_type
            print(product.assign_to_content_type)
            product.assign_to_object_id = recipient.id
            print(product.assign_to_object_id)
            product.save()
            # AssetAssignment kaydını oluşturuyoruz
            assign_by_content_type = ContentType.objects.get_for_model(request.user.__class__)
            print(assign_by_content_type)
            assign_to_content_type = ContentType.objects.get_for_model(recipient.__class__)
            print(assign_to_content_type)

            # Create the AssetAssignment instance
            asset_assignment = AssetAssignment.objects.create(
                company=company,
                product=product,
                assign_by_content_type=assign_by_content_type,  # ContentType for the assign_by user
                assign_by_object_id=request.user.id,  # ID of the assigning user
                assign_to_content_type=assign_to_content_type,  # ContentType for the assign_to user
                assign_to_object_id=recipient.id,  # ID of the assigned user
                info=info,
                assign_date=assign_date,
                return_status=None,
                appointed_company=appointed_company,
                appointed_address=appointed_address,
                batch_id=batch_id,  # Same batch_id used
                is_active=True,
            )

            # Save the instance (although save() is redundant when using .create())
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


def add_brand_view(request, company_code):
    """
    Marka eklemek için
    """
    print('Add branda geldi')
    company = get_object_or_404(Company, code=company_code)

    if request.method == 'POST':
        form = BrandForm(request.POST, company=company)
        if form.is_valid():
            brand_name = form.cleaned_data['name']

            # Aynı şirkette aynı isimde marka var mı kontrol et
            if Brand.objects.filter(company=company, name__iexact=brand_name).exists():
                return JsonResponse({'success': False, 'errors': {'name': ['Bu isimde bir marka zaten mevcut.']}}, status=400)

            brand = form.save(commit=False)
            brand.company = company
            brand.created_by = request.user
            brand.save()
            return JsonResponse({'success': True, 'message': 'Marka başarıyla eklendi!'})

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def add_model_view(request, company_code):
    company = get_company(company_code)
    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.company = company
            model.is_active = True
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
    categories = Category.objects.filter(company=company)
    brand_form = BrandForm(company=company)
    product_status_form = ProductStatusForm()
    model_form = ModelForm(company=company)
    brands = Brand.objects.filter(company=request.user.company)
    return render(request, 'manage_entities.html', {
        'brands':brands,
        'categories':categories,
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
from django.core.paginator import Paginator
def companies(request):
    if request.user.company.code != settings.MASTER_COMPANY:
        messages.error(request, "Lütfen ürünleri ve bir kullanıcı seçin.")
        return redirect('company_dashboard', request.user.company.code)

    add_company_form = CompanyCreateForm()

    # Tüm şirketleri al ve paginator kullan
    company_list = Company.objects.all()
    paginator = Paginator(company_list, 10)  # Sayfa başına 10 şirket gösterilecek

    # `page` parametresini al
    page_number = request.GET.get('page')
    companies = paginator.get_page(page_number)

    context = {
        'add_company_form': add_company_form,
        'companies': companies,
    }
    return render(request, 'companies.html', context)
def check_code(request, code):
    # Veritabanında aynı koda sahip bir şirket var mı diye kontrol et
    exists = Company.objects.filter(code=code).exists()
    
    # JSON olarak yanıt döndür
    return JsonResponse({'exists': exists})
def available_products(request, company_code):
    """
    Henüz zimmetlenmemiş ürünleri getirir
    """
    print()
    company = get_company(company_code)
    # Correct way to check for null values in assing_to field
    assignments_items = Product.objects.filter(company=company, assign_to__isnull=True)
    print(assignments_items)
    return render(request, 'available_products.html', {'assignments_items': assignments_items})
from django.db.models import Q
from django.core.serializers import serialize
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.serializers import serialize
from django.db.models import Q
from .models import Product, Company
@login_required


def get_products(request, company_code):
    search = request.GET.get('search', '')
    
    try:
        company = Company.objects.get(code=company_code)
        products = Product.objects.select_related('category', 'brand', 'model').filter(company__code=company_code)

        if search:
            products = products.filter(name__icontains=search)

        # Serileştirilmiş ürün verilerini al
        product_data = list(products.values(
            'category__name', 
            'brand__name', 
            'model__name', 
            'serial_number', 
            'model__unit', 
            'status'
        ))

        total_products = products.count()  # Toplam ürün sayısını al

        return product_data, total_products  # Hem ürün verisi hem de toplam ürün sayısını döndürüyoruz

    except Company.DoesNotExist:
        return [], 0  # Şirket bulunamazsa boş veri ve 0 döndürüyoruz

# def get_unassigned_products(request, company_code):
#     # Zimmetlenmemiş ürünleri filtrelemek için get_products fonksiyonunu kullan
#     products = get_products(request, company_code)

#     # Zimmetlenmemiş ürünleri filtrele
#     unassigned_products = products.filter(
#         Q(assign_by_content_type__isnull=True, assign_to_content_type__isnull=True)
#     )
    
#     unassigned_count = unassigned_products.count()

#     return unassigned_products, unassigned_count  # Zimmetlenmemiş ürünler ve sayısını döndürür
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def admin_dashboard(request, company_code):
    """
        Yönetici Alanını açar
    """
    check_company_code(request, company_code)  # Şirket kodunu kontrol eder.

    # Şirket ve ürünleri al
    products, total_products = get_products(request, company_code)  # Hem ürün verisi hem de toplam ürün sayısı döner
    company = get_company(company_code)

    assignments = AssetAssignment.objects.select_related('product', 'assign_to_content_type', 'assign_by_content_type')\
                                         .filter(company=company).order_by('-created_at')[:5]

    # Kullanıcıları al ve sayfalama ekle
    if request.user.company.code != settings.MASTER_COMPANY:
        users = LdapUser.objects.filter(company=request.user.company).order_by('-username')
    else:
        users = CustomUser.objects.all().order_by('username')

    paginator = Paginator(users, 10)  # Sayfa başına 10 kullanıcı
    page_number = request.GET.get('page')

    try:
        paginated_users = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_users = paginator.page(1)
    except EmptyPage:
        paginated_users = paginator.page(paginator.num_pages)
    print(paginated_users)
    # Context verileri
    context = {
        'total_products':total_products,
        'assignments': assignments,
        'products': products,
        'users': paginated_users,  # Sayfalı kullanıcılar
        'user_count': paginator.count,  # Toplam kullanıcı sayısı
        'paginator': paginator,  # Paginator nesnesi
    }

    # Admin dashboard sayfasını render et
    return render(request, 'admin_area/admin_dashboard.html', context)


from ldap3 import Server, Connection, ALL
from ldap3 import MODIFY_REPLACE
# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
from time import sleep
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, NTLM
import logging
from time import sleep
from django.shortcuts import get_object_or_404
from .models import LdapConfig  # Model yolu doğru olmalı
from django.contrib.auth.models import User

from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, NTLM
import logging
from time import sleep
from django.shortcuts import get_object_or_404
from .models import LdapConfig  # LdapConfig modelinizi buraya göre ayarlayın.


def create_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Django'da kullanıcı oluştur
        try:
            user = LdapUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            print(f"Kullanıcı oluşturuldu: {username}")
            
            # LDAP sunucusuna kullanıcıyı ekle
            if create_user_in_ldap(user):  # Sadece kullanıcıyı gönderiyoruz
                messages.success(request, "Kullanıcı LDAP sunucusuna başarıyla eklendi.")
            else:
                messages.warning(request, "Kullanıcı LDAP sunucusuna eklenemedi.")
            
            return redirect("create_user_view")
        
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {str(e)}")
            print(f"create_user_view Hatası: {str(e)}")

    return render(request, "create_user.html")
def create_user_in_ldap(django_user):
    """
    Django kullanıcısını LDAP sunucusuna ekler ve gerekli özellikleri atar.
    """
    try:
        print(f"create_user_in_ldap çağrıldı: {django_user.username}")
        
        # LDAP sunucu bilgilerini al
        company = get_object_or_404(Company,id=2)
        ldap_config = get_object_or_404(LdapConfig, company = company  )
        ldap_server = ldap_config.ldap_server
        ldap_username = ldap_config.bind_username
        ldap_password = ldap_config.bind_password
        ldap_domain = ldap_config.bind_dn

        # LDAP bağlantısı kur
        server = Server(ldap_server, get_info=ALL)
        connection = None

        for attempt in range(3):  # 3 defa tekrar dene
            try:
                connection = Connection(
                    server,
                    user=f"{ldap_domain}\\{ldap_username}",
                    password=ldap_password,
                    authentication=NTLM,
                    auto_bind=True
                )
                if connection.bind():
                    print("LDAP bağlantısı başarılı.")
                    break
            except Exception as e:
                print(f"LDAP bağlantı denemesi {attempt + 1} başarısız: {str(e)}")
                if attempt == 2:  # 3 kez denedikten sonra hata ver
                    raise e
                sleep(5)
        
        if not connection or not connection.bound:
            print("LDAP bağlantısı kurulamadı.")
            return False

        # Kullanıcı bilgilerini hazırla
        user_dn = f"cn={django_user.username},ou=Users,dc=example,dc=com"
        attributes = {
            "objectClass": ["top", "person", "organizationalPerson", "user"],
            "cn": django_user.username,
            "sn": django_user.last_name or "NoLastName",
            "givenName": django_user.first_name or "NoFirstName",
            "displayName": f"{django_user.first_name} {django_user.last_name}",
            "mail": django_user.email or "noemail@example.com",  # Varsayılan email
            "userPassword": "default_password",
        }

        # Kullanıcıyı LDAP sunucusuna ekle
        if connection.add(user_dn, attributes=attributes):
            print(f"Kullanıcı LDAP sunucusuna başarıyla eklendi: {django_user.username}")
        else:
            print(f"Kullanıcı ekleme hatası: {connection.result['description']}")
            return False

        # Hesabın kilidini aç
        connection.extend.microsoft.unlock_account(user=user_dn)
        print(f"Hesap açıldı: {django_user.username}")

        # Şifreyi ayarla
        new_password = "new_password"
        connection.extend.microsoft.modify_password(user=user_dn, new_password=new_password)
        print(f"Şifre ayarlandı: {django_user.username}")

        # userAccountControl ve pwdLastSet değerlerini ayarla
        connection.modify(user_dn, changes={
            "userAccountControl": (MODIFY_REPLACE, [512]),
            "pwdLastSet": (MODIFY_REPLACE, [0]),
        })
        print(f"userAccountControl ve pwdLastSet güncellendi: {django_user.username}")

        return True

    except Exception as e:
        print(f"LDAP işleminde hata oluştu: {str(e)}")
        return False

# REPORTS 
def user_based_asset(request, company_code):
    # Şirketi getir
    company = get_company(company_code)

    # Kullanıcı şirket koduna göre filtreleme
    if request.user.company.code == settings.MASTER_COMPANY:
        # MASTER_COMPANY'ye bağlı kullanıcılar
        users = CustomUser.objects.filter(company=company)
    else:
        # Diğer şirketlerdeki LDAP kullanıcıları
        users = LdapUser.objects.filter(company=company)

    # Bağlam (context) oluştur
    context = {
        'users': users,
        'company': company,
    }

    # Şablonu render et
    return render(request, 'reports/user_based_asset.html', context)
def calendar(request):
    users = LdapUser.objects.all()
    context = {
        'users':users,
    }
    return render(request,'admin_area/calendar1.html',context)
from django.shortcuts import render
from django.http import JsonResponse
from .models import Category, Product  # Product içinde brand ve model var

from django.shortcuts import render
from django.http import JsonResponse
from .models import Category, Product  # Product modelinde brand ve model var

from django.shortcuts import render
from .models import Category, Product

def list_categories(request, company_code):
    # Şirketi al
    company = get_company(company_code)

    # Filtreleme için başlangıçta boş liste
    categories = []
    brands = []
    models = []

    # Geçerli olmayan bir filtreleme seçeneği varsa, uyarı mesajı ekle
    valid_filters = ['category', 'brands', 'models']

    if request.method == "GET":
        # Eğer geçerli olmayan bir parametre varsa
        invalid_filters = [key for key in request.GET.keys() if key not in valid_filters]
        if invalid_filters:
            # Geçersiz parametre varsa, uyarı mesajı göster
            messages.error(request, f"Bu seçenekler: {', '.join(invalid_filters)} bulunmuyor.")

        if request.GET.get('category'):  # Kategoriler
            categories = Category.objects.filter(company=company)
        if request.GET.get('brands'):  # Markalar
            brands = Brand.objects.filter(company=company)
        if request.GET.get('models'):  # Modeller
            models = Model.objects.filter(company=company)

    context = {
        'categories': categories,
        'brands': brands,
        'models': models
    }

    return render(request, 'list/list_categories.html', context)


