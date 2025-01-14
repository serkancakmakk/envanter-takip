function loadBrands(categoryId) {
    $.ajax({
        url: `/api/get_brands_api/${companyCode}/?category_id=${categoryId}`,
        type: "GET",
        success: function (response) {
            let brands = response.brands;
            let brandSelect = $("#new-brand-select"); // Markalar dropdown'ı
            let brandTableBody = $("#brand-table-body"); // Markalar tablosu
            console.log('js çalıştır',categoryId)
            // Markalar yüklendikten sonra, formu temizle ve seçenekleri ekle
            brandSelect.empty().append('<option value="">Select Brand</option>');
            brandTableBody.empty();

            if (brands.length === 0) {
                Swal.fire({
                    icon: 'info',
                    title: 'Bilgi',
                    text: 'Belirtilen kategoride marka bulunamadı.',
                });
            } else {
                // Her marka için seçeneği ve tabloyu doldur
                brands.forEach(function (brand) {
                    brandSelect.append(`<option value="${brand.id}">${brand.name}</option>`);
                    brandTableBody.append(`
                        <tr>
                            <td>${brand.id}</td>
                            <td>${brand.name}</td>
                            <td>${brand.category_name}</td>
                        </tr>
                    `);
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // Sunucudan dönen hata mesajını kontrol et
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
                    text: `Markalar yüklenirken bir hata oluştuq. ${textStatus}: ${errorThrown}`,
                });
            }
        }
    });
}

// Kategori seçildiğinde markaları yükle
$("#new-category-select").change(function () { // Burada doğru elementin ID'si `new-category-select`
    var categoryId = $(this).val();
    console.log(categoryId)
    if (categoryId) {
        loadBrands(categoryId); // Kategoriyi seçtikten sonra markaları yükle
    } else {
        $("#product-brand").empty().append('<option value="">Select Brand</option>');
        $("#product-model").empty().append('<option value="">Select Model</option>');
    }
});
