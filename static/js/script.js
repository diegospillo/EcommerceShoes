document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.newsletter form');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const emailInput = document.querySelector('#email');
            if (emailInput.value.trim() !== '') {
                alert('Grazie per esserti iscritto!');
                emailInput.value = '';
            }
        });
    }
});