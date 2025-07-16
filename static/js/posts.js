document.addEventListener('DOMContentLoaded', function() {
    // Handle Like functionality
    const likeForms = document.querySelectorAll('.like-comment form');

    likeForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = this.action;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    const newLikeCount = data.new_like_count;
                    const likeButton = this.querySelector('button');
                    const likeCountSpan = this.querySelector('span');

                    likeButton.style.color = 'blue';
                    likeCountSpan.textContent = newLikeCount;
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    // Handle Comment functionality
    const commentForms = document.querySelectorAll('form[action*="comment_post"]');

    commentForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = this.action;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    this.querySelector('input[type="text"]').value = '';
                    const newCommentCount = data.new_comment_count;
                    const commentCountSpan = this.querySelector('span');
                    commentCountSpan.textContent = newCommentCount;
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
});
