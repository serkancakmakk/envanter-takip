from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.urls import resolve
from .models import Company

# inventory_track/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

import logging

import logging
from django.urls import resolve
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

class CheckCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)

        # URL'den company_code parametresini kontrol edin
        path_info = request.path_info
        try:
            resolver_match = resolve(path_info)
            company_code = resolver_match.kwargs.get('company_code', None)
        except Exception as e:
            
            company_code = None

        # Master kullanıcı kontrolü
        if request.user.company.code == settings.MASTER_COMPANY and request.user.tag == settings.MASTER_TAG:
            
            return self.get_response(request)

        # Şirket kodu doğrulama
        if company_code and request.user.company.code != company_code:
           
            messages.error(request, "Kendi firmanıza yönlendirildiniz.")
            return redirect('company_dashboard', company_code=request.user.company.code)

        return self.get_response(request)
