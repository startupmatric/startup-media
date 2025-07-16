// scripts/upload.js

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('input[type="file"]');

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const fileType = file.type;
            if (!['image/jpeg', 'image/png', 'video/mp4'].includes(fileType)) {
                alert('Invalid file type! Please upload an image or video.');
                fileInput.value = ''; // Clear the file input
            }
        }
    });
});
