$(document).ready(function () {
    // Kategorileri yükleme fonksiyonu
    function loadCategories() {
        $.ajax({
            url: `/api/get_categories_api/${companyCode}/`,
            type: "GET",
            success: function (response) {
                let categories = response.categories;
                let categorySelect = $("#new-category-select");
                let categoryTableBody = $("#category-table-body2");

                // Select ve tabloyu temizle
                categorySelect.empty().append('<option value="">Kategori Seç</option>');
                categoryTableBody.empty();

                // Her kategori için seçenek ve tablo satırı ekle
                categories.forEach(category => {
                    categorySelect.append(`<option value="${category.id}">${category.category_name}</option>`);
                    categoryTableBody.append(`
                        <tr>
                            <td>${category.id}</td>
                            <td>${category.category_name}</td>
                            <td>
                                <button type="button" class="btn btn-warning delete-category-btn" 
                                    data-id="${category.id}" 
                                    data-name="${category.category_name}">
                                    Sil
                                </button>
                            </td>
                        </tr>
                    `);
                });

                // DataTable yeniden başlat
                initializeDataTable();
            },
            error: function () {
                errorSwal("Kategori verileri yüklenirken bir hata oluştu.");
            }
        });
    }

    // DataTable başlatma fonksiyonu
    function initializeDataTable() {
        if ($.fn.DataTable.isDataTable('#category-table')) {
            $('#category-table').DataTable().destroy();
        }
        $('#category-table').DataTable();
    }

    // Kategoriyi ekleme fonksiyonu
    function addCategory(e) {
        e.preventDefault();
        let categoryName = $("#new-category-name").val().trim();
        let url = $(this).data("url");
        let csrfToken = $("input[name='csrfmiddlewaretoken']").val();

        // Kategori adı boş olmamalı
        if (!categoryName) {
            return errorSwal("Kategori adı boş olamaz.");
        }

        $.ajax({
            url: url,
            type: "POST",
            data: {
                name: categoryName,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (response) {
                if (response.success) {
                    successSwal(response.message);
                    $("#new-category-name").val("");
                    loadCategories();
                } else {
                    errorSwal(response.message);
                }
            },
            error: function () {
                errorSwal("Kategori eklenirken bir hata oluştu.");
            }
        });
    }

    // Kategoriyi silme fonksiyonu
    $(document).on('click', '.delete-category-btn', function () {
        let categoryId = $(this).data('id');
        let categoryName = $(this).data('name');
        let csrfToken = $("meta[name='csrf-token']").attr("content");

        // Kullanıcı onayı al
        Swal.fire({
            title: `${categoryName} kategorisini silmek istediğinizden emin misiniz?`,
            text: "Bu işlem geri alınamaz!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Evet, Sil',
            cancelButtonText: 'Hayır, İptal Et',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/api/delete_category_api/${categoryId}/`,
                    type: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    success: function (response) {
                        Swal.fire(
                            'Silindi!',
                            `${categoryName} kategorisi başarıyla silindi.`,
                            'success'
                        );
                        loadCategories();
                    },
                    error: function () {
                        Swal.fire(
                            'Hata!',
                            'Silme işlemi sırasında bir hata oluştu.',
                            'error'
                        );
                    }
                });
            } else if (result.dismiss === Swal.DismissReason.cancel) {
                Swal.fire(
                    'İptal Edildi',
                    'Silme işlemi iptal edildi.',
                    'info'
                );
            }
        });
    });

    // Sayfa yüklendiğinde kategorileri yükle
    loadCategories();

    // Form gönderiminde kategoriyi ekle
    $("#category-form").on("submit", addCategory);
});
