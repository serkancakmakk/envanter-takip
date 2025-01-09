from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

def company_required(view_func):
    def wrapper(request, *args, **kwargs):
        company_code = kwargs.get('company_code')

        print('Decoratora geldi')

        # Eğer kullanıcı master şirketine aitse her yere erişim izni verilir
        if request.user.company.code == settings.MASTER_COMPANY:
            return view_func(request, *args, **kwargs)

        # Kullanıcının şirket kodu ile istenen şirket kodu eşleşmiyorsa
        if request.user.company.code != company_code:
            messages.info(request, 'Sadece kendi şirketinizde işlem yapabilirsiniz.')
            return redirect('company_dashboard', request.user.company.code)
        
        return view_func(request, *args, **kwargs)
    return wrapper