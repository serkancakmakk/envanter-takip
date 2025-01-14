 // Add New Brand
 $("#brand-form").on("submit", function (e) {
    e.preventDefault();
    let categoryId = $("#new-category-select").val();
    let brandName = $("#new-brand-name").val();
    let url = $(this).data("url");
    var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url: url,
        type: "POST",
        data: {
            category: categoryId,
            name: brandName,
            csrfmiddlewaretoken: csrfToken,
        },
        success: function () {
            successSwal("Marka başarıyla eklendi.");
            $("#new-brand-name").val("");
            loadBrands(categoryId);
        },
        error: function () {
            errorSwal("Marka eklenirken bir hata oluştu.");
        }
    });
});
