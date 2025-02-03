// loadCategoryOptions.js
$(document).ready(function () {
    const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    const companyCode = $("#company-code").val(); // Şirket kodunu HTML içinden al

    /** 📌 Yeni Kategori Dropdown Seçeneklerini Yükle (Sadece Gerekli Olduğunda) */
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

    // 📌 Yeni kategori eklendiğinde dropdown seçeneklerini güncelle
    loadCategoryOptions();
});