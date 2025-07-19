document.addEventListener('DOMContentLoaded', function() {
    // Rating stars
    const stars = document.querySelectorAll('.rating i');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.getAttribute('data-value');
            document.querySelector('input[name="rating"]').value = rating;
            
            stars.forEach(s => {
                if (s.getAttribute('data-value') <= rating) {
                    s.classList.add('bi-star-fill');
                    s.classList.remove('bi-star');
                } else {
                    s.classList.add('bi-star');
                    s.classList.remove('bi-star-fill');
                }
            });
        });
    });
});