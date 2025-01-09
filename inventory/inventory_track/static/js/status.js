$(document).ready(function () {
    const companyCode = $('#company-code').val(); // Şirket kodunu al

    // Durumları Yükle
    function loadStatuses() {
        $.ajax({
            url: `/api/get_statutes_api/${companyCode}/`,
            type: 'GET',
            success: function (response) {
                $('#status-table-body').empty(); // Tabloyu temizle
                // Durumları tabloya ekle
                response.statuses.forEach(status => {
                    $('#status-table-body').append(`
                        <tr>
                            <td>${status.id}</td>
                            <td>${status.name}</td>
                        </tr>
                    `);
                });
            },
            error: function () {
                Swal.fire('Hata', 'Durumlar yüklenirken bir sorun oluştu!', 'error');
            }
        });
    }
 // Yeni Durum Kaydet
 $('#status-form').on('submit', function (e) {
    e.preventDefault();
    const statusName = $('#new-status-name').val(); // Durum adını al
    $.ajax({
        url: `/api/create_status_api/${companyCode}/`,  // Şirket kodunu URL'ye ekle
        type: 'POST',
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'), // CSRF token
        },
        data: {
            name: statusName,
        },
        success: function () {
            Swal.fire('Başarılı', 'Durum başarıyla kaydedildi!', 'success');
            loadStatuses(); // Durumları yeniden yükle
            $('#new-status-name').val(''); // Giriş alanını temizle
        },
        error: function () {
            Swal.fire('Hata', 'Durum kaydedilirken bir sorun oluştu!', 'error');
        }
    });
});

loadStatuses(); // Sayfa yüklendiğinde durumları yükle
});