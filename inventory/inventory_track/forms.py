
from django import forms
from .models import Brand, Category, Company, CustomUser, LdapUser, Model, Product,ProductStatus,LdapConfig
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

from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifrenizi girin',
            'class': 'form-control',
        }),
        label="Şifre",
        min_length=8,  # Minimum şifre uzunluğu
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifrenizi tekrar girin',
            'class': 'form-control',
        }),
        label="Şifre (Tekrar)",
    )

    class Meta:
        """
        Custom user sadece destek kullanıcıları içindir.
        """
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kullanıcı adı'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
        }
        labels = {
            'username': mark_safe('<strong>Kullanıcı Adı</strong>'),
            'email': mark_safe('<strong>E-Posta Adresi</strong>'),
            'first_name': mark_safe('<strong>Ad</strong>'),
            'last_name': mark_safe('<strong>Soyad</strong>'),
            'phone': mark_safe('<strong>Telefon Numarası</strong>'),
        }


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Şifreler eşleşmiyor. Lütfen tekrar deneyin.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Şifreyi hashleyin
        if commit:
            user.save()
        return user
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'is_active']

    # Telefon alanı için ek özellikler (örneğin, uzunluk kontrolü, regex vb.)
    phone = forms.CharField(max_length=15, required=False, label="Telefon", widget=forms.TextInput(attrs={'placeholder': 'Telefon numarasını girin'}))

    # Formdaki verilerin doğruluğunu kontrol etme (isteğe bağlı)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Telefon numarasıyla ilgili ek doğrulamalar yapılabilir
        return phone

    # Formu kaydederken özel işlemler yapılabilir
    def save(self, commit=True):
        user = super().save(commit=False)
        # Eğer commit=False ise, veritabanına kaydetmeden önce düzenlemeler yapılabilir
        if commit:
            user.save()
        return user