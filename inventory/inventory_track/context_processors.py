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
    company_code = None  # Default olarak None değeri veriyoruz
    if request.user.is_authenticated:
        try:
            company_code = request.user.company.code
        except AttributeError:
            # Eğer 'company' özelliği mevcut değilse, company_code'yu None bırakıyoruz
            company_code = None
    return {'company_code': company_code}