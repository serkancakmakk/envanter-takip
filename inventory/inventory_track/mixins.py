# myapp/mixins.py
from django.shortcuts import get_object_or_404
from .models import Company
def get_company(company_code):
    """
    Şirket bilgisini almak için kullanılacak fonksiyon.
    """
    return get_object_or_404(Company, code=company_code)
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from .models import Company
def check_company_permission(view_func):
    def _wrapped_view(request, *args, **kwargs):
        company_code = kwargs.get('company_code')  # URL'den gelen company_code
        print(company_code)
        # Master kullanıcı kontrolü
        if request.user.company.code == settings.MASTER_COMPANY and request.user.tag == settings.MASTER_TAG:
            try:
                Company.objects.get(code=company_code)
            except Company.DoesNotExist:
                messages.error(request, "Geçersiz şirket kodu. Lütfen tekrar kontrol edin.")
                return redirect('inventory', company_code=request.user.company.code)
        else:
            # Normal kullanıcı kontrolü
            if request.user.company.code != company_code:
                messages.error(request, "Kendi firmanıza yönlendirildiniz.")
                return redirect('inventory', company_code=request.user.company.code)

        return view_func(request, *args, **kwargs)

    return _wrapped_view