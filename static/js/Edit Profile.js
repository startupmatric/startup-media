document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;

        if (!username || !email) {
            event.preventDefault();
            alert('Please fill out all required fields.');
        }
    });
});
