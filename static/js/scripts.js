function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

$(document).ready(function () {
    $('#contact-form').submit(function (e) {
        e.preventDefault();  // Prevent the default form submission

        $.ajax({
            type: "POST",
            url: "{{ url_for('submit_form') }}",
            data: $(this).serialize(),
            success: function (response) {
                alert(response);  // Display a popup notification with the response
            },
            error: function (xhr, status, error) {
                alert("Error: Could not submit the form.");  // Display an error popup
            }
        });
    });

    $('#send-email-btn').click(function () {
        $.ajax({
            type: "POST",
            url: "{{ url_for('send_email_route') }}",
            data: {
                search_term: '{{ search_term }}',
            },
            success: function (response) {
                alert(response);
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });
    });
});
