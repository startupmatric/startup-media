document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const username = document.getElementById('username');
    const password = document.getElementById('password');

    form.addEventListener('submit', function (event) {
        let valid = true;

        if (username.value.trim() === '') {
            valid = false;
            username.style.borderColor = 'red';
        } else {
            username.style.borderColor = '#ddd';
        }

        if (password.value.trim() === '') {
            valid = false;
            password.style.borderColor = 'red';
        } else {
            password.style.borderColor = '#ddd';
        }

        if (!valid) {
            event.preventDefault();
            alert('Please fill in all fields.');
        }
    });
});
