document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.querySelector('.carousel-wrapper');
    const cards = document.querySelectorAll('.carousel-card');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    let currentIndex = 0;
    const cardWidth = cards[0].offsetWidth + 20; // Card width + margin

    // Update Carousel Position
    const updateCarousel = () => {
        wrapper.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
    };

    // Next Button Click
    nextBtn.addEventListener('click', () => {
        if (currentIndex < cards.length - 1) {
            currentIndex++;
            updateCarousel();
        }
    });

    // Previous Button Click
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });
});
