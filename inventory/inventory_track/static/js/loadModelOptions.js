$(document).ready(function () {
    const companyCode = $("#company-code").val(); // Şirket kodunu al

    /** 📌 Kategori Dropdown Seçeneklerini Yükle */
    function loadCategoryOptions() {
        $.get(`/api/get_categories_api/${companyCode}/`, { all: true })
            .done(function (response) {
                let categorySelect = $("#new-category-select").empty().append('<option value="">Kategori Seç</option>');
                response.categories.forEach(category => {
                    categorySelect.append(`<option value="${category.id}">${category.category_name}</option>`);
                });
            })
            .fail(() => errorSwal("Kategoriler yüklenirken bir hata oluştu."));
    }

    /** 📌 Seçilen Kategoriye Göre Marka Getir */
    function loadBrandOptions(categoryId) {
        if (!categoryId) {
            $("#new-brand-select").empty().append('<option value="">Önce kategori seçin</option>');
            $("#new-model-select").empty().append('<option value="">Önce marka seçin</option>');
            return;
        }

        $.get(`/api/get_brands_api/${companyCode}/`, { category_id: categoryId })
            .done(function (response) {
                let brandSelect = $("#new-brand-select").empty().append('<option value="">Marka Seç</option>');
                response.brands.forEach(brand => {
                    brandSelect.append(`<option value="${brand.id}">${brand.name}</option>`);
                });
            })
            .fail(() => errorSwal("Markalar yüklenirken bir hata oluştu."));
    }

    /** 📌 Seçilen Markaya Göre Model Getir */
    function loadModelOptions(brandId) {
        if (!brandId) {
            $("#new-model-select").empty().append('<option value="">Önce marka seçin</option>');
            return;
        }

        $.get(`/api/get_models_api/${companyCode}/`, { brand_id: brandId })
            .done(function (response) {
                let modelSelect = $("#new-model-select").empty().append('<option value="">Model Seç</option>');
                response.models.forEach(model => {
                    modelSelect.append(`<option value="${model.id}">${model.name}</option>`);
                });
            })
            .fail(() => errorSwal("Modeller yüklenirken bir hata oluştu."));
    }

    // 📌 Sayfa yüklendiğinde kategorileri getir
    loadCategoryOptions();

    // 📌 Kategori seçildiğinde ilgili markaları getir
    $("#new-category-select").on("change", function () {
        let selectedCategoryId = $(this).val();
        loadBrandOptions(selectedCategoryId);
        $("#new-model-select").empty().append('<option value="">Önce marka seçin</option>'); // Model dropdown'u sıfırla
    });

    // 📌 Marka seçildiğinde ilgili modelleri getir
    $("#new-brand-select").on("change", function () {
        let selectedBrandId = $(this).val();
        loadModelOptions(selectedBrandId);
    });
});
