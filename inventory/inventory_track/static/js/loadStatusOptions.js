$(document).ready(function () {
    const companyCode = $("#company-code").val(); // Şirket kodunu al

    /** 📌 Şirketin durum seçeneklerini getir ve dropdown'a ekle */
    function loadStatusOptions() {
        $.get(`/api/get_statutes_api/${companyCode}/`)
            .done(function (response) {
                let statusSelect = $("#status-select").empty().append('<option value="">Durum Seç</option>');
                response.statuses.forEach(status => {
                    statusSelect.append(`<option value="${status.id}">${status.name}</option>`);
                });
            })
            .fail(() => errorSwal("Durumlar yüklenirken bir hata oluştu."));
    }

    // 📌 Sayfa yüklendiğinde durumları getir
    loadStatusOptions();
});