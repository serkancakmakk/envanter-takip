from django.conf import settings

def add_user_permissions(request):
    if request.user.is_authenticated:
        is_master = (
            request.user.company.code == settings.MASTER_COMPANY
            and request.user.tag == settings.MASTER_TAG
        )
    else:
        is_master = False

    return {
        'is_master': is_master,
    }
def company_code(request):
    company_code = None
    if request.user.is_authenticated:
        if 'company_code' in request.resolver_match.kwargs:  # URL'den company_code'yu al
            company_code = request.resolver_match.kwargs['company_code']
        else:
            try:
                # Kullanıcının şirket kodunu al
                company_code = request.user.company.code
            except AttributeError:
                company_code = None
    return {'company_code': company_code}
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def master_company(request):
    return {
        'MASTER_COMPANY': os.getenv('MASTER_COMPANY')
    }