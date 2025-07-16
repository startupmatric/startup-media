// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // Handle Like Button Clicks
    document.querySelectorAll('.post form[action*="like_post"]').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting the usual way
            const postId = this.action.split('/').pop(); // Extract the post ID
            const likeButton = this.querySelector('button');

            // Make an AJAX request to like the post
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the like count displayed on the post
                    const likeCount = this.nextElementSibling;
                    likeCount.textContent = `${data.like_count} likes`;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle Comment Submissions
    document.querySelectorAll('.post form[action="/comment_post"]').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting the usual way
            const postId = this.querySelector('input[name="post_id"]').value;
            const commentContent = this.querySelector('input[name="content"]').value;

            // Make an AJAX request to submit the comment
            fetch('/comment_post', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ post_id: postId, content: commentContent })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Append the new comment to the post's comment section
                    const commentSection = this.parentElement.querySelector('.comments-section');
                    const newComment = document.createElement('p');
                    newComment.textContent = `${data.username}: ${commentContent}`;
                    commentSection.appendChild(newComment);
                    this.querySelector('input[name="content"]').value = ''; // Clear the comment input field
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Dynamically load more posts (optional feature)
    let loadMoreButton = document.getElementById('load-more-posts');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function() {
            fetch('/load_more_posts', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Append new posts to the post feed
                    const postFeed = document.querySelector('.post-feed');
                    data.posts.forEach(post => {
                        const newPost = document.createElement('div');
                        newPost.className = 'post';
                        newPost.innerHTML = `
                            <p><strong>${post.username}</strong> <small>${post.timestamp}</small></p>
                            <p>${post.content}</p>
                            <form action="/like_post/${post.id}" method="post" style="display:inline;">
                                <button type="submit">Like</button>
                            </form>
                            <p>${post.like_count} likes</p>
                            <form action="/comment_post" method="post">
                                <input type="hidden" name="post_id" value="${post.id}">
                                <input type="text" name="content" placeholder="Add a comment" required>
                                <button type="submit">Comment</button>
                            </form>
                            <p>${post.comment_count} comments</p>
                        `;
                        postFeed.appendChild(newPost);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

});
