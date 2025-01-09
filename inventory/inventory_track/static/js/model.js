$(document).ready(function () {
    // Formun gönderimini AJAX ile işleme
    $("#model-form").on("submit", function (e) {
        e.preventDefault(); // Sayfa yenilenmesini engelle
        console.log('Form gönderiliyor');

        // Form URL'ini ve CSRF token'ını al
        var url = $(this).attr("action"); // URL formdan alınır
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

        // Form verilerini al
        let brandId = $("#new-brand-select").val();
        let modelName = $("#new-model-name").val();
        let unitName = $("#unit-name").val();
        let companyCode = $("#company-code").val(); // company code hidden input

        // AJAX isteği gönder
        $.ajax({
            url: url,
            type: "POST",
            data: {
                brand: brandId,
                name: modelName,
                unit: unitName,
                company_code: companyCode, // company_code'yu AJAX verisine ekle
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                // Başarı mesajı
                Swal.fire({
                    icon: "success",
                    title: "Başarılı",
                    text: "Model başarıyla eklendi!"
                });

                // Modelleri tekrar yükle
                loadModels(brandId); // model ekledikten sonra ilgili markaya ait modelleri yükle

                // Form inputlarını temizle
                $("#new-brand-select").val("");
                $("#new-model-name").val("");
                $("#unit-name").val("");
            },
            error: function (xhr, status, error) {
                console.error("Hata:", error);
                Swal.fire({
                    icon: "error",
                    title: "Hata",
                    text: "Model eklenirken bir hata oluştu."
                });
            }
        });
    });

    // Marka seçildiğinde modelleri yükle
    $("#new-brand-select").on("change", function () {
        let brandId = $(this).val();
        if (brandId) {
            loadModels(brandId); // Marka seçildiyse modelleri yükle
        } else {
            clearModels(); // Marka seçimi kaldırılırsa modeli temizle
        }
    });
});

// Modelleri yükleyen fonksiyon
function loadModels(brandId) {
    let companyCode = $("#company-code").val(); // company code hidden input

    $.ajax({
        url: `/api/get_models_api/${companyCode}/`, // Dinamik URL
        type: "GET",
        data: { brand_id: brandId },
        success: function (response) {
            let models = response.models;
            console.log('Modeller alındı');

            // Tablo ve dropdown'u temizle
            let modelTableBody = $("#model-table-body");
            let modelSelect = $("#new-model-select");

            modelTableBody.empty();
            modelSelect.empty();

            // Dropdown'a varsayılan bir seçenek ekle
            modelSelect.append('<option value="">Model Seç</option>');

            // Gelen modelleri tabloya ve dropdown'a ekle
            models.forEach(model => {
                // Tabloya ekleme
                modelTableBody.append(`
                    <tr>
                        <td>${model.id}</td>
                        <td>${model.name}</td>
                        <td>${model.brand_name}</td>
                        <td>${model.category_name}</td>
                    </tr>
                `);

                // Dropdown'a ekleme
                modelSelect.append(`
                    <option value="${model.id}">${model.name}</option>
                `);
            });
        },
        error: function () {
            errorSwal("Modeller yüklenirken bir hata oluştu.");
        }
    });
}

// Modelleri temizleyen fonksiyon
function clearModels() {
    $("#model-table-body").empty();
    $("#new-model-select").empty().append('<option value="">Model Seç</option>');
}