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
    product_model = serializers.CharField(source='product.model.name', read_only=True)
    assign_by_details = serializers.SerializerMethodField()
    assign_to_details = serializers.SerializerMethodField()
    localized_assign_date = serializers.SerializerMethodField()
    class Meta:
        model = AssetAssignment
        fields = '__all__'

    def get_assign_by_details(self, obj):
        if obj.assign_by_content_type and obj.assign_by_object_id:
            assign_by_instance = obj.assign_by
            if assign_by_instance:
                return {
                    "id": obj.assign_by_object_id,
                    "type": obj.assign_by_content_type.model,  # İçerik türünü belirler
                    "name": getattr(assign_by_instance, 'username', str(assign_by_instance)),
                    "email": getattr(assign_by_instance, 'email', None)
                }
        return None
    def get_localized_assign_date(self, obj):
        return obj.assign_date.strftime("%d %B %Y")  # Türkçe aylar için yerelleştirme
    def get_assign_to_details(self, obj):
        if obj.assign_to_content_type and obj.assign_to_object_id:
            assign_to_instance = obj.assign_to
            if assign_to_instance:
                return {
                    "id": obj.assign_to_object_id,
                    "type": obj.assign_to_content_type.model,  # İçerik türünü belirler
                    "name": getattr(assign_to_instance, 'username', str(assign_to_instance)),
                    "email": getattr(assign_to_instance, 'email', None)
                }
        return None