$(document).ready(function () {
    // Ürün ekleme formunun gönderilmesini AJAX ile işleme
    $("#product-form").on("submit", function (e) {
        e.preventDefault(); // Sayfa yenilenmesini engelle
        var url = $(this).data("url");
        $.ajax({
            url: url, // Doğru URL'yi kontrol edin
            type: "POST",
            data: $(this).serialize(), // Form verilerini serialize ederek gönder
            success: function (response) {
                if (response.success) {
                    // Yeni ürünü tabloya ekle
                    var product = response.product;
                    var newRow = `
                        <tr>
                            <td>${product.id}</td>
                            <td>${product.category}</td>
                            <td>${product.brand}</td>
                            <td>${product.model}</td>
                            <td>${product.serial_number}</td>
                            <td>${product.status}</td>
                            <td>${product.date_joined}</td>
                            <td>${product.created_by}</td>
                        </tr>
                    `;
                    $("#product-table-body").append(newRow);

                    // Formu sıfırla
                    $("#product-form")[0].reset();

                    // Başarı mesajı göster
                    Swal.fire({
                        icon: 'success',
                        title: 'Başarılı',
                        text: 'Ürün başarıyla eklendi!',
                        timer: 2000, // Mesajın otomatik kapanması için
                        showConfirmButton: false
                    });
                } else {
                    // Hata mesajı göster
                    Swal.fire({
                        icon: 'error',
                        title: 'Hata',
                        text: response.error || 'Bir sorun oluştu.',
                    });
                }
            },
            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: 'Sunucuyla iletişimde bir sorun oluştu.',
                });
            }
        });
    });
});
