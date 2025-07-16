document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const email = document.getElementById('email');
    const role = document.getElementById('role');

    form.addEventListener('submit', function (event) {
        let valid = true;
        
        if (username.value.trim() === '') {
            valid = false;
            username.style.borderColor = 'red';
        } else {
            username.style.borderColor = '#ddd';
        }
        
        if (password.value.trim() === '' || password.value.length < 6) {
            valid = false;
            password.style.borderColor = 'red';
        } else {
            password.style.borderColor = '#ddd';
        }
        
        if (email.value.trim() === '' || !validateEmail(email.value)) {
            valid = false;
            email.style.borderColor = 'red';
        } else {
            email.style.borderColor = '#ddd';
        }

        if (!valid) {
            event.preventDefault();
            alert('Please correct the errors in the form.');
        }
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});
