document.addEventListener("DOMContentLoaded", function() {
    const userCheckboxes = document.querySelectorAll('.userCheckbox');
    const selectedUsersContainer = document.getElementById('selectedUsers');
    const receiverIdsInput = document.getElementById('receiver_ids');
    const messageInput = document.querySelector('#messageForm input[name="content"]');

    userCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedUsers();
        });
    });

    function updateSelectedUsers() {
        selectedUsersContainer.innerHTML = '';
        const selectedUsers = [];
        userCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const username = checkbox.dataset.username;
                selectedUsers.push(checkbox.value);
                const userChip = document.createElement('span');
                userChip.classList.add('selected-user');
                userChip.textContent = username;
                selectedUsersContainer.appendChild(userChip);
            }
        });
        receiverIdsInput.value = selectedUsers.join(',');
    }

    // Clear message input after form submit
    const messageForm = document.getElementById('messageForm');
    messageForm.addEventListener('submit', function(event) {
        messageInput.value = ''; // Clear input field
    });
});
