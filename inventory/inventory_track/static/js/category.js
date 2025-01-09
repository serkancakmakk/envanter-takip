$(document).ready(function () {
    // Kategorileri yükleme fonksiyonu
    function loadCategories() {
        $.ajax({
            url: `/api/get_categories_api/${companyCode}/`,
            type: "GET",
            success: function (response) {
                let categories = response.categories;
                let categorySelect = $("#new-category-select");
                let categoryTableBody = $("#category-table-body");

                // Seçenekleri temizle
                categorySelect.empty().append('<option class="form-select" value="">Kategori Seç</option>');
                categoryTableBody.empty();

                // Her kategori için seçenek ekle
                categories.forEach(category => {
                    categorySelect.append(`<option class="form-select" value="${category.id}">${category.category_name}</option>`);
                    categoryTableBody.append(`
                        <tr>
                            <td>${category.id}</td>
                            <td>${category.category_name}</td>
                            <td>
                                <button type="submit" class="btn btn-warning delete-category-btn" data-id="${category.id}" data-name="${category.category_name}">Sil</button>
                            </td>
                        </tr>
                    `);
                });
            },
            error: function () {
                errorSwal("Kategori verileri yüklenirken bir hata oluştu.");
            }
        });
    }

    // Kategoriyi ekleme fonksiyonu
    function addCategory(e) {
        e.preventDefault();
        let categoryName = $("#new-category-name").val();
        let url = $(this).data("url");
        let csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        
        // Kategori adı boş olmamalı
        if (!categoryName.trim()) {
            return errorSwal("Kategori adı boş olamaz.");
        }

        $.ajax({
            url: url,  // İlgili kategori ekleme URL'si
            type: "POST",
            data: {
                name: categoryName,
                csrfmiddlewaretoken: csrfToken,  // CSRF token
            },
            success: function (response) {
                if (response.success) {
                    successSwal(response.message);  // Başarı mesajı
                    $("#new-category-name").val("");  // Input alanını temizle
                    loadCategories();  // Kategorileri yenile
                } else {
                    errorSwal(response.message);  // Hata mesajı (örneğin kategori zaten mevcut)
                }
            },
            error: function () {
                errorSwal("Kategori eklenirken bir hata oluştu.");
            }
        });
    }

    // Kategori formunu dinle
    $("#category-form").on("submit", addCategory);  // Kategori ekleme fonksiyonunu burada çağırıyoruz

    // Sayfa yüklendiğinde kategorileri yükle
    loadCategories();

    // CSRF token'ını meta etiketinden al
    $(document).on('click', '.delete-category-btn', function () {
        var categoryId = $(this).data('id');
        var categoryName = $(this).data('name');  // data-name ile kategori adını alıyoruz
        var csrfToken = $("meta[name='csrf-token']").attr("content");
        // Swal ile kullanıcıdan onay alma
        Swal.fire({
            title: `${categoryName} kategorisini silmek istediğinizden emin misiniz. Bu kategoriye bağlı tüm marka modellerde silinecektir? `,
            text: "Bu işlem geri alınamaz!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Evet, Sil',
            cancelButtonText: 'Hayır, İptal Et',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                // Onay verildiğinde kategori silme işlemini yap
                $.ajax({
                    url: `/api/delete_category_api/${categoryId}/`,
                    type: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken  // CSRF token'ı header olarak ekleyin
                    },
                    success: function(response) {
                        // Başarı mesajı ve kategoriler listesine güncelleme
                        Swal.fire(
                            'Silindi!',
                            `${categoryName} kategorisi başarıyla silindi.`,
                            'success'
                        );
                        loadCategories();  // Kategorileri yeniden yükle
                    },
                    error: function() {
                        // Hata mesajı
                        Swal.fire(
                            'Hata!',
                            'Silme işlemi sırasında bir hata oluştu.',
                            'error'
                        );
                    }
                });
            } else if (result.dismiss === Swal.DismissReason.cancel) {
                // İptal edildiğinde herhangi bir şey yapma
                Swal.fire(
                    'İptal Edildi',
                    'Silme işlemi iptal edildi.',
                    'info'
                );
            }
        });
    });
    
    
});
