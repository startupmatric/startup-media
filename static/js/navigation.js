// scripts/navigation.js

document.addEventListener('DOMContentLoaded', () => {
    const settingsButton = document.querySelector('li a[href="#"]'); // Assuming settings is the last item
    const settingsMenu = document.querySelector('.settings-menu');

    settingsButton.addEventListener('click', (event) => {
        event.preventDefault();
        settingsMenu.classList.toggle('show'); // Toggle visibility of settings menu
    });
});
