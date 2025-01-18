from rest_framework import serializers
from inventory_track.models import AssetAssignment, Company, Product

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'city', 'country', 'code']
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')  # category modelinden name alanını al
    class Meta:
        model = Product
        fields = ['id', 'brand', 'category_name', 'model', 'serial_number']  # Hangi alanların döneceğini belirtiyoruz
# serializers.py
from rest_framework import serializers
from inventory_track.models import AssetAssignment

class AssetAssignmentSerializer(serializers.ModelSerializer):
    product_category = serializers.CharField(source='product.category.name', read_only=True)
    class Meta:
        model = AssetAssignment
        fields = '__all__'  # Gerekli alanları belirtin
