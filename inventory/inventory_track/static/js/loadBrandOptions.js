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

    // 📌 Sayfa yüklendiğinde kategorileri getir
    loadCategoryOptions();

    // 📌 Kategori seçildiğinde ilgili markaları getir
    $("#new-category-select").on("change", function () {
        let selectedCategoryId = $(this).val();
        loadBrandOptions(selectedCategoryId);
    });
});
