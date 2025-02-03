// loadCategories.js
$(document).ready(function () {
    let currentPage = 1;
    const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    const companyCode = $("#company-code").val(); // Şirket kodunu HTML içinden al

    /** 📌 Kategori Listesini Sayfalama ile Yükle */
    function loadCategories(page = 1) {
        $.get(`/api/get_categories_api/${companyCode}/`, { page })
            .done(function (response) {
                let categoryList = $(".category-list").empty();
                let pagination = $(".category-pagination").empty();
                let categoryOption = $(".category-select").empty();

                if (response.categories.length > 0) {
                    response.categories.forEach(category => {
                        categoryList.append(`
                            <div class="category-card d-flex justify-content-between align-items-center p-2 mb-2 rounded bg-light">
                                <span class="fw-semibold">${category.category_name}</span>
                                <button type="button" class="btn btn-sm btn-danger delete-category-btn" data-id="${category.id}" data-name="${category.category_name}">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        `);
                    });
                } else {
                    categoryList.append('<p class="text-muted text-center">Henüz kategori eklenmemiş.</p>');
                }

                // 🔹 Sayfalama Butonları
                if (response.total_pages > 1) {
                    for (let i = 1; i <= response.total_pages; i++) {
                        pagination.append(`<li class="page-item ${i === page ? 'active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`);
                    }
                }
            })
            .fail(() => errorSwal("Kategori verileri yüklenirken bir hata oluştu."));
    }

    /** 📌 Sayfa Değiştirildiğinde (Kategori Listesi için) */
    $(document).on("click", ".category-pagination .page-link", function (e) {
        e.preventDefault();
        currentPage = $(this).data("page");
        loadCategories(currentPage);
    });

    // 📌 Sayfa Yüklendiğinde Kategori Listesini Getir
    loadCategories();
});
