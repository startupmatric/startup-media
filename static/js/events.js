<!-- Firebase SDKs -->
<script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-database.js"></script>

<script>
  // Your web app's Firebase configuration
  const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    databaseURL: "YOUR_DATABASE_URL",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  
  const db = firebase.database();
  
  // Function to send message
  function sendMessage() {
      const message = document.getElementById('messageInput').value;
      const username = "{{ session['username'] if session.get('loggedin') else 'Guest' }}";
      db.ref('chats/{{ event.id }}').push({
          username: username,
          message: message,
          timestamp: new Date().toISOString()
      });
      document.getElementById('messageInput').value = '';
  }
  
  // Listen for new messages
  db.ref('chats/{{ event.id }}').on('child_added', function(snapshot) {
      const chat = snapshot.val();
      const chatContainer = document.getElementById('chatContainer');
      const chatMessage = document.createElement('p');
      chatMessage.innerHTML = `<strong>${chat.username}:</strong> ${chat.message}`;
      chatContainer.appendChild(chatMessage);
  });
</script>
