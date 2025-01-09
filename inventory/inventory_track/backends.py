import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from ldap3 import Server, Connection, ALL, NTLM
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from .models import Company, LdapConfig, LdapUser

logger = logging.getLogger(__name__)

from django.contrib import messages
from ldap3 import Server, Connection, ALL, NTLM
from django.shortcuts import get_object_or_404
import logging
from ldap3 import Server, Connection, ALL, NTLM   # LDAPSocketOpenError'ı ekledik
from django.contrib import messages
from django.shortcuts import get_object_or_404
import logging
from django.contrib.auth.backends import BaseBackend
logger = logging.getLogger(__name__)

from ldap3 import Server, Connection, ALL, NTLM
from django.contrib import messages
from django.shortcuts import get_object_or_404
import logging

from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPSocketOpenError, LDAPExceptionError

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.backends import BaseBackend
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Company, CustomUser
from django.conf import settings
from ldap3 import Server, Connection, ALL
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)

class LDAPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, company_code=None):
        # Kullanıcı bilgilerini kontrol et
        print('ldapa geldi')
        print('kad',username)
        print('kad',password)
        print('kad',company_code)
        if username is None or password is None or company_code is None:
            if request:
                messages.error(request, "Kullanıcı adı, şifre veya şirket kodu eksik.")
            return None

        # Şirketin LDAP bilgilerini al
        try:
            company = Company.objects.get(code=company_code)
        except Company.DoesNotExist:
            logger.error(f"Geçersiz şirket kodu: {company_code}")
            if request:
                messages.error(request, "Geçersiz şirket kodu. Lütfen kontrol edin.")
            return None

        ldap_config = get_object_or_404(LdapConfig, company=company)
        ldap_server = ldap_config.ldap_server
        ldap_domain = ldap_config.base_dn

        # LDAP bağlantısını yap
        try:
            server = Server(ldap_server, get_info=ALL)
            conn = Connection(server, user=f"{ldap_domain}\\{username}", password=password, authentication=NTLM)

            # LDAP doğrulamasını kontrol et
            if conn.bind():
                # Kullanıcıyı oluştur veya getir
                user, created = LdapUser.objects.get_or_create(username=username,company=company)

                # Eğer kullanıcı yeni oluşturulduysa şirket bilgisi ekle
                if created:
                    user.company = company  # Şirket bilgisi ekleniyor
                    user.set_password(password)
                    user.save()

                # Kullanıcının şirketini doğrula
                if user.company != company:
                    logger.error(f"Kullanıcı şirketi uyuşmuyor: {username} - {user.company.code} yerine {company_code}")
                    if request:
                        messages.error(request, "Bu şirkete giriş izniniz yok.")
                    return None

                return user
            else:
                logger.error(f"LDAP doğrulaması başarısız: {username}")
                if request:
                    messages.error(request, "LDAP doğrulaması başarısız. Lütfen bilgilerinizi kontrol edin.")
                return None

        # LDAP sunucu bağlantı hatasını kontrol et
        except LDAPSocketOpenError:
            logger.error("LDAP sunucusuna bağlantı sağlanamadı.")
            if request:
                messages.error(request, "LDAP sunucusuna bağlanılamadı. Lütfen sistem yöneticinize başvurun.")
            return None

        # Diğer LDAP hatalarını yakala
        except LDAPExceptionError as e:
            logger.error(f"LDAP hatası: {e}")
            if request:
                messages.error(request, "LDAP bağlantısı sırasında bir hata oluştu.")
            return None

        # Genel bir hata yakalanırsa
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            if request:
                messages.error(request, "Bir hata oluştu. Lütfen tekrar deneyin.")
            return None

    def get_user(self, user_id):
        """
        Kullanıcıyı ID'siyle getir
        """
        try:
            return LdapUser.objects.get(pk=user_id)
        except LdapUser.DoesNotExist:
            return None

from django.contrib.auth.backends import ModelBackend
from inventory_track.models import CustomUser

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, company_code=None):
        try:
            # Kullanıcıyı bul
            user = CustomUser.objects.get(username=username)
            
            # Şifreyi kontrol et
            if user.check_password(password):
                return user
            return None
        except CustomUser.DoesNotExist:
            return None