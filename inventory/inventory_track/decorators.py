from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

def check_company_code(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Eğer kullanıcı giriş yapmamışsa, yönlendirme yapılabilir
        if not request.user.is_authenticated:
            return redirect('login')  # Giriş yapmamış kullanıcıyı login sayfasına yönlendir

        # Eğer kullanıcı şirket kodu ile yetkilendirilmemişse, hata mesajı ekleyip yönlendirme yap
        if request.user.company.code != settings.MASTER_COMPANY:
            messages.error(request, 'Bu sayfaya erişim izniniz yok.')
            return redirect('company_dashboard', request.user.company.code)

        # Şirket kodu doğruysa, normal işlem devam eder
        return view_func(request, *args, **kwargs)

    return _wrapped_view


