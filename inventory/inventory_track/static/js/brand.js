function loadBrands(categoryId, page = 1) {
    $.ajax({
        url: `/api/get_brands_api/${companyCode}/?category_id=${categoryId}&page=${page}`,
        type: "GET",

        success: function (response) {
            console.log('API Yanıtı:', response); // Gelen veriyi kontrol et

            let brands = response.brands;
            if (!brands || !Array.isArray(brands)) {
                console.error("Hatalı yanıt formatı:", response);
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: 'API yanıtında beklenen formatta veri bulunamadı.',
                });
                return;
            }

            let brandSelect = $("#new-brand-select"); // Marka dropdown
            let brandList = $(".brand-list"); // Marka liste alanı
            let paginationContainer = $(".brand-pagination"); // Sayfalama alanı
            console.log('JS çalıştırıldı, Kategori ID:', categoryId);

            // Temizleme işlemleri
            brandSelect.empty().append('<option value="">Marka Seç</option>');
            brandList.empty();
            paginationContainer.empty();

            // Eğer gelen marka listesi boşsa kullanıcıya bildirim ver
            if (brands.length === 0) {
                Swal.fire({
                    icon: 'info',
                    title: 'Bilgi',
                    text: 'Bu kategoride marka bulunmamaktadır.',
                });
                return;
            }

            // Dropdown'a markaları ekle
            brands.forEach(function (brand) {
                if (!brand.id || !brand.name) {
                    console.error("Eksik marka verisi:", brand);
                    return;
                }

                brandSelect.append(`<option value="${brand.id}">${brand.name}</option>`);
                brandList.append(`
                    <div class="category-card d-flex justify-content-between align-items-center p-2 mb-2 rounded bg-light">
                                <span class="fw-semibold">${brand.name} ${brand.category_name || "Bilinmeyen Kategori"}</span>
                                <button type="button" class="btn btn-sm btn-danger delete-category-btn" 
                                    data-id="${brand.id}" data-name="${brand.name}">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                `);
            });

            // Sayfalama butonlarını oluştur
            createPagination(response.total_pages, response.current_page, categoryId);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("API Hata:", textStatus, errorThrown);
            if (jqXHR.status === 404) {
                Swal.fire({
                    icon: 'info',
                    title: 'Bilgi',
                    text: 'Belirtilen kategoride marka bulunamadı.',
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: `Markalar yüklenirken bir hata oluştu. ${textStatus}: ${errorThrown}`,
                });
            }
        }
    });
}

// Sayfalama butonlarını oluşturma fonksiyonu
function createPagination(totalPages, currentPage, categoryId) {
    let paginationContainer = $(".brand-pagination");
    paginationContainer.empty();

    if (totalPages < 2) {
        return; // Eğer tek sayfa varsa sayfalama butonlarını oluşturma
    }

    for (let page = 1; page <= totalPages; page++) {
        let activeClass = page === currentPage ? "active" : "";
        paginationContainer.append(`
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" data-page="${page}">${page}</a>
            </li>
        `);
    }

    // Sayfalama butonlarına tıklama eventi
    $(".brand-pagination .page-link").off("click").on("click", function (e) {
        e.preventDefault();
        let selectedPage = $(this).data("page");
        loadBrands(categoryId, selectedPage);
    });
}

// Kategori seçildiğinde markaları yükle
$("#new-category-select").change(function () {
    let categoryId = $(this).val();
    console.log("Seçilen kategori ID:", categoryId);

    if (categoryId) {
        loadBrands(categoryId); // Kategori değiştiğinde markaları yükle
    } else {
        $(".brand-list").empty();
        $(".brand-pagination").empty();
        $("#new-brand-select").empty().append('<option value="">Marka Seç</option>');
    }
});
$(document).ready(function () {
    $("#new-brand-select").on("change", function () {
        let brandId = $(this).val();
        let companyCode = $("#company-code").val();

        if (!brandId) {
            $("#model-table-body").empty(); // Seçim kaldırıldıysa tabloyu temizle
            return;
        }

        $.ajax({
            url: `/api/get_models_api/${companyCode}/?brand_id=${brandId}`,
            type: "GET",
            success: function (response) {
                console.log("Model API Yanıtı:", response); // Hata ayıklamak için

                if (response.models && response.models.length > 0) {
                    $("#model-table-body").empty();
                    response.models.forEach(function (model) {
                        $("#model-table-body").append(`
                            <tr>
                                <td>${model.id}</td>
                                <td>${model.name}</td>
                                <td>${model.brand_name}</td>
                                <td>${model.category_name}</td>
                            </tr>
                        `);
                    });
                } else {
                    $("#model-table-body").html('<tr><td colspan="4">Bu marka için model bulunamadı.</td></tr>');
                }
            },
            error: function () {
                Swal.fire({
                    icon: "error",
                    title: "Hata",
                    text: "Modeller yüklenirken hata oluştu."
                });
            }
        });
    });
});
