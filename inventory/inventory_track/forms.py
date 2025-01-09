
from django import forms
from .models import Brand, Category, Company, LdapUser, Model, Product,ProductStatus,LdapConfig
# for company
class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['company', 'category', 'brand', 'model', 'serial_number']  # Formda gösterilecek alanlar
class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'code', 'address', 'phone', 'email', 'city', 'country', 'owner']
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # Telefon numarasını string'e çevir (bu adım hatayı giderir)
        phone = str(phone)

        # Telefon numarasının sadece rakamlardan oluştuğundan emin olun
        if not phone.isdigit():
            raise forms.ValidationError("Telefon numarası yalnızca rakamlardan oluşmalıdır.")
        
        # Telefon numarasının uzunluğunun 11 karakter olduğundan emin olun
        if len(phone) != 11:
            raise forms.ValidationError("Telefon numarası 11 haneli olmalıdır.")
        
        return phone
    # Ekstra doğrulamalar veya alanlar eklemek isterseniz burada yapılabilir
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Company.objects.filter(code=code).exists():
            raise forms.ValidationError("Bu şirket kodu zaten mevcut.")
        return code
from django import forms
from .models import LdapConfig

class LdapConfigForm(forms.ModelForm):
    class Meta:
        model = LdapConfig
        fields = ['ldap_server', 'ldap_port', 'base_dn', 'bind_username', 'bind_dn', 'bind_password']
        
    # Alanlar zorunlu değil
    ldap_port = forms.CharField(required=False)
    bind_dn = forms.CharField(required=False)
    base_dn = forms.CharField(required=False)
    bind_username = forms.CharField(required=False)
    bind_password = forms.CharField(required=False, widget=forms.PasswordInput)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_active']  # Şirketi formdan kaldırdık, çünkü otomatik atanacak

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            # Şirket bilgisine göre kategoriler zaten ekleme anında atanacağı için burada ek bir işlem yok
            pass

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['category','name', 'is_active']  # Şirketi formdan kaldırdık, çünkü otomatik atanacak

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            # Şirket bilgisine göre markalar otomatik atanacak
            pass

class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['brand', 'name', 'is_active','unit']  # Şirketi formdan kaldırdık, çünkü otomatik atanacak

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            # Şirket bilgisine göre markaları filtrele
            self.fields['brand'].queryset = Brand.objects.filter(company=company)
class ProductStatusForm(forms.ModelForm):
    class Meta:
        model = ProductStatus
        fields = ['name']
class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = LdapUser
        fields = ['email','email_password']