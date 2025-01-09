from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import redirect
from .models import Company, CustomUser, LdapConfig, LdapUser
from django.conf import settings

def authenticate_user(request, company_code, username, password):
    """Kullanıcıyı doğrulama ve giriş işlemleri"""
    print("authenticate_user çağrıldı.")
    try:
        # Şirket kodunu kontrol et
        company = Company.objects.get(code=company_code)
    except Company.DoesNotExist:
        # Geçersiz şirket kodu
        messages.error(request, "Geçersiz şirket kodu.")
        return None, 'invalid_company'

    # Şirkete bağlı LDAP konfigürasyonu var mı?
    ldap_configs = LdapConfig.objects.filter(company=company).first()
    if not ldap_configs:
        messages.error(request, "LDAP yapılandırması bulunamadı.")
        return None, 'no_ldap_config'

    try:
        # LDAP doğrulama
        user = authenticate(request, username=username, password=password, company_code=company_code)
        if user:
            # Kullanıcı doğrulandı
            ldap_user, created = LdapUser.objects.get_or_create(username=username, company_code=company_code)
            if not ldap_user.password:
                ldap_user.set_password(password)
                ldap_user.save()
            return ldap_user, 'authenticated'

        # Kullanıcı adı veya şifre hatalı
        messages.error(request, "Kullanıcı adı veya şifre hatalı.")
        return None, 'invalid_credentials'

    except Exception as e:
        # LDAP sunucusuna bağlanılamadı
        print(f"LDAP bağlantı hatası: {e}")
        messages.error(request, "LDAP sunucusuna bağlanılamadı. Lütfen sistem yöneticinize başvurun.")
        return None, 'ldap_connection_error'
def authenticate_custom_user(request, company_code, username, password):
    try:
        # Şirketi bul
        company = Company.objects.get(code=company_code)

        # Kullanıcıyı CustomUserManager üzerinden doğrulama
        user = CustomUser.objects.get_by_natural_key(username=username)
        ### ss
        # Şifreyi kontrol et
        if user.check_password(password):
            return user, 'custom_user'
        else:
            return None, 'invalid_credentials'
    except CustomUser.DoesNotExist:
        return None, 'user_not_found'
    except Company.DoesNotExist:
        return None, 'company_not_found'