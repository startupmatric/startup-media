from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
from MySQLdb.cursors import DictCursor
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from waitress import serve
app = Flask(__name__)
def get_db_connection():
    return mysql.connection.cursor(DictCursor)

# Set the folder for uploads
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Limit allowed file extensions for security
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app.secret_key = 'Yash@9390'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'DBMS2004'
app.config['MYSQL_DB'] = 'startup_matric'

# Configuration for file uploads
mysql = MySQL(app)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = account['role']
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password!')
            return redirect(url_for('login'))

    return render_template('login_signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # e.g., Startup, Investor, etc.

        cursor = mysql.connection.cursor(DictCursor)
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)',
                (username, email, password, role)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Signup successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            flash(f'Error during signup: {e}')
            return redirect(url_for('signup'))

    return render_template('login_signup.html')
@app.route('/index')
def index():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch posts and associated users
        cursor.execute('''
            SELECT posts.id, posts.content, posts.timestamp, users.username, posts.user_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.timestamp DESC
        ''')
        posts = cursor.fetchall()

        for post in posts:
            cursor.execute('SELECT image_path FROM post_images WHERE post_id = %s', (post['id'],))
            post['images'] = cursor.fetchall()

            cursor.execute('SELECT COUNT(*) AS like_count FROM likes WHERE post_id = %s', (post['id'],))
            post['like_count'] = cursor.fetchone()['like_count']

            cursor.execute('SELECT COUNT(*) AS comment_count FROM comments WHERE post_id = %s', (post['id'],))
            post['comment_count'] = cursor.fetchone()['comment_count']

            cursor.execute('''
                SELECT status FROM network_requests
                WHERE requester_id = %s AND target_user_id = %s
            ''', (session['id'], post['user_id']))
            request_status = cursor.fetchone()
            post['network_status'] = request_status['status'] if request_status else None

            cursor.execute('SELECT * FROM likes WHERE user_id = %s AND post_id = %s', (session['id'], post['id']))
            post['liked'] = cursor.fetchone() is not None

        cursor.execute('SELECT title, summary, thumbnail, link FROM news ORDER BY publish_date DESC LIMIT 5')
        news_items = cursor.fetchall()
        return render_template('index.html', posts=posts,news_items=news_items)
    return redirect(url_for('login'))

@app.route('/post', methods=['POST'])
def create_post():
    if 'loggedin' in session:
        content = request.form.get('content')
        images = request.files.getlist('images')  # Get multiple images

        if content:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO posts (user_id, content, timestamp) VALUES (%s, %s, NOW())', 
                           (session['id'], content))
            post_id = cursor.lastrowid  # Get the last inserted post ID

            # Save uploaded images
            for image in images:
                image_path = save_image(image)
                if image_path:
                    cursor.execute('INSERT INTO post_images (post_id, image_path) VALUES (%s, %s)', (post_id, image_path))

            mysql.connection.commit()
            cursor.close()
            return jsonify(success=True)

        return jsonify(success=False, message="Content cannot be empty.")
    return jsonify(success=False, message="User not logged in.")

def save_image(image):
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        return filename  # Return the relative path to the image
    return None
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('INSERT INTO likes (user_id, post_id) VALUES (%s, %s)', (session['id'], post_id))
            mysql.connection.commit()

            # Get the new like count
            cursor.execute('SELECT COUNT(*) AS like_count FROM likes WHERE post_id = %s', (post_id,))
            new_like_count = cursor.fetchone()['like_count']

            return f'success, new_like_count: {new_like_count}'  # Returning plain text
        except MySQLdb.IntegrityError:
            return 'error, message: You have already liked this post.'  # Returning plain text
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            return f'error, message: {str(e)}'  # Returning plain text
        finally:
            cursor.close()

    return 'error, message: You need to log in to like a post.'  # Returning plain text

@app.route('/comment_post', methods=['POST'])
def comment_post():
    if 'loggedin' in session:
        post_id = request.form.get('post_id')
        content = request.form.get('content')

        if post_id and content.strip():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute('INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)',
                               (session['id'], post_id, content))
                mysql.connection.commit()

                # Get the new comment count
                cursor.execute('SELECT COUNT(*) AS comment_count FROM comments WHERE post_id = %s', (post_id,))
                new_comment_count = cursor.fetchone()['comment_count']

                return f'success, comment_content: {content}, username: {session["username"]}, new_comment_count: {new_comment_count}'  # Returning plain text
            except MySQLdb.Error as e:
                mysql.connection.rollback()
                return f'error, message: {str(e)}'  # Returning plain text
            finally:
                cursor.close()

        return 'error, message: Invalid input.'  # Returning plain text

    return 'error, message: You need to log in to comment.'  # Returning plain text
@app.route('/profile/<username>')
def user_profile(username):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch individual user details
        cursor.execute('''
            SELECT id, username, email, role, bio, linkedin, website, contact_info, about,
                   expertise, experience, location, avatar
            FROM users WHERE username = %s
        ''', (username,))
        account = cursor.fetchone()

        if not account:
            cursor.close()
            return 'User not found', 404

        # Fetch user skills and experiences
        cursor.execute('SELECT skill FROM skills WHERE user_id = %s', (account['id'],))
        skills = cursor.fetchall()

        cursor.execute('SELECT title, company FROM experiences WHERE user_id = %s', (account['id'],))
        experiences = cursor.fetchall()

        # Fetch network count
        cursor.execute('SELECT COUNT(*) AS network_count FROM network_requests WHERE target_user_id = %s AND status = "accepted"', (account['id'],))
        network_count = cursor.fetchone()['network_count']

        # Fetch startup details if user is a founder
        startup = None
        if account['role'] == 'startup':
            cursor.execute('''
                SELECT name, description, location, logo AS avatar, funding_needed, vision, mission, employees
                FROM startups WHERE user_id = %s
            ''', (account['id'],))
            startup = cursor.fetchone()

        cursor.close()

        return render_template(
            'profile.html',
            user=account,
            skills=skills,
            experiences=experiences,
            network_count=network_count,
            startup=startup
        )
    
    return redirect(url_for('login'))
@app.route('/update_about', methods=['POST'])
def update_about():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        about_info = request.form.get('about')
        
        # Update the "About" section in the database
        cursor.execute('UPDATE users SET about = %s WHERE id = %s', (about_info, session['id']))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('user_profile', username=session['username']))

    return redirect(url_for('login'))

@app.route('/update_features', methods=['POST'])
def update_features():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Retrieve values from the form
        product_demo = request.form.get('product_demo')
        milestones = request.form.get('milestones')
        funding_stage = request.form.get('funding_stage')
        investment_focus = request.form.get('investment_focus')
        portfolio = request.form.get('portfolio')
        expertise = request.form.get('expertise')
        experience = request.form.get('experience')

        # Update the specific fields based on the user's role
        if session['role'] == 'startup':
            cursor.execute('''
                UPDATE users 
                SET product_demo = %s, milestones = %s, funding_stage = %s 
                WHERE id = %s
            ''', (product_demo, milestones, funding_stage, session['id']))
        elif session['role'] == 'investor':
            cursor.execute('''
                UPDATE users 
                SET investment_focus = %s, portfolio = %s 
                WHERE id = %s
            ''', (investment_focus, portfolio, session['id']))
        elif session['role'] == 'mentor':
            cursor.execute('''
                UPDATE users 
                SET expertise = %s, experience = %s 
                WHERE id = %s
            ''', (expertise, experience, session['id']))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('user_profile', username=session['username']))

    return redirect(url_for('login'))
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Fetching the data from the form
            username = request.form.get('username')
            email = request.form.get('email')
            role = request.form.get('role')
            bio = request.form.get('bio')
            linkedin = request.form.get('linkedin')
            website = request.form.get('website')
            contact_info = request.form.get('contact_info')

            # Update user profile in the database, including the new fields
            cursor.execute('''
                UPDATE users 
                SET username = %s, email = %s, role = %s, bio = %s, linkedin = %s, website = %s, contact_info = %s 
                WHERE id = %s
            ''', (username, email, role, bio, linkedin, website, contact_info, session['id']))
            mysql.connection.commit()

            return redirect(url_for('user_profile', username=session['username']))

        # Fetch current user details, including the new fields
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()

        return render_template('edit_profile.html', account=account)

    return redirect(url_for('login'))

@app.route('/connections/<int:user_id>')
def view_connections(user_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch only accepted network requests
        cursor.execute('''
            SELECT DISTINCT u.id, u.username 
            FROM network_requests nr 
            JOIN users u ON nr.requester_id = u.id 
            WHERE nr.target_user_id = %s AND nr.status = 'accepted'
        ''', (user_id,))
        accepted_connections = cursor.fetchall()

        cursor.close()
        return render_template('connections.html', connections=accepted_connections)
    return redirect(url_for('login'))
@app.route('/remove_connection/<int:user_id>', methods=['POST'])
def remove_connection(user_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Remove connection by setting status to 'removed' or deleting the request
        try:
            cursor.execute('''
                DELETE FROM network_requests 
                WHERE (requester_id = %s AND target_user_id = %s) OR 
                      (requester_id = %s AND target_user_id = %s)
            ''', (session['id'], user_id, user_id, session['id']))
            mysql.connection.commit()
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()
            cursor.close()
            return f'Error: {e}'

        cursor.close()
        return redirect(url_for('view_connections', user_id=session['id']))
    
    return redirect(url_for('login'))

# Route for viewing network requests
@app.route('/network_requests')
def network_requests():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch incoming requests where the logged-in user is the target
        cursor.execute('''
            SELECT nr.id, u.username AS requester_username
            FROM network_requests nr
            JOIN users u ON nr.requester_id = u.id
            WHERE nr.target_user_id = %s AND nr.status = 'pending'
        ''', (session['id'],))
        incoming_requests = cursor.fetchall()

        # Fetch outgoing requests where the logged-in user is the requester
        cursor.execute('''
            SELECT nr.id, u.username AS target_username, nr.status
            FROM network_requests nr
            JOIN users u ON nr.target_user_id = u.id
            WHERE nr.requester_id = %s
        ''', (session['id'],))
        outgoing_requests = cursor.fetchall()

        cursor.close()
        return render_template('network_requests.html', 
                               incoming_requests=incoming_requests, 
                               outgoing_requests=outgoing_requests)
    return redirect(url_for('login'))
@app.route('/network_request/<int:user_id>', methods=['POST'])
def network_request(user_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)
        
        # Check if a request already exists (pending or accepted)
        cursor.execute('''
            SELECT * FROM network_requests 
            WHERE requester_id = %s AND target_user_id = %s
        ''', (session['id'], user_id))
        existing_request = cursor.fetchone()
        
        if existing_request:
            cursor.close()
            if existing_request['status'] == 'accepted':
                return 'You are already connected to this user.'
            return 'You have already sent a request to this user.'

        try:
            # Insert the network request if none exists
            cursor.execute('INSERT INTO network_requests (requester_id, target_user_id, status) VALUES (%s, %s, %s)', 
                           (session['id'], user_id, 'pending'))
            mysql.connection.commit()
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()
            cursor.close()
            return f'Error: {e}'
        
        cursor.close()
        return redirect(url_for('index'))
    
    return redirect(url_for('login'))

# Route for accepting a network request
@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Update the request to "accepted"
        cursor.execute('''
            UPDATE network_requests 
            SET status = 'accepted' 
            WHERE id = %s AND target_user_id = %s
        ''', (request_id, session['id']))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('network_requests'))
    return redirect(url_for('login'))
# Route for rejecting a network request
@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Update the request to "rejected"
        cursor.execute('''
            UPDATE network_requests 
            SET status = 'rejected' 
            WHERE id = %s AND target_user_id = %s
        ''', (request_id, session['id']))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('network_requests'))
    return redirect(url_for('login'))
# Route for messaging
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(DictCursor)

        # Handle sending a message
        if request.method == 'POST':
            receiver_id = request.form['receiver_id']
            content = request.form['content']
            try:
                cursor.execute('''
                    INSERT INTO messages (sender_id, receiver_id, content, timestamp) 
                    VALUES (%s, %s, %s, NOW())
                ''', (session['id'], receiver_id, content))
                mysql.connection.commit()
            except MySQLdb.Error as e:
                mysql.connection.rollback()
                cursor.close()
                return f'Error: {e}'
            cursor.close()
            return redirect(url_for('messages', chat_partner_id=receiver_id))

        # Handle searching for users
        query = request.args.get('query')
        search_results = []
        if query:
            cursor.execute('SELECT id, username FROM users WHERE username LIKE %s', ('%' + query + '%',))
            search_results = cursor.fetchall()

        # Retrieve user's conversations (distinct users they've messaged with)
        cursor.execute('''
            SELECT u.id, u.username, MAX(m.timestamp) AS last_timestamp
            FROM messages m
            JOIN users u ON (m.sender_id = u.id OR m.receiver_id = u.id)
            WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.id != %s
            GROUP BY u.id, u.username
            ORDER BY last_timestamp DESC
        ''', (session['id'], session['id'], session['id']))
        conversations = cursor.fetchall()

        # Retrieve messages with a specific chat partner if selected
        chat_partner_id = request.args.get('chat_partner_id')
        chat_partner = None
        messages = []
        if chat_partner_id:
            # Get the chat partner's info
            cursor.execute('SELECT id, username FROM users WHERE id = %s', (chat_partner_id,))
            chat_partner = cursor.fetchone()

            # Get the messages between the user and the selected chat partner
            cursor.execute('''
                SELECT sender_id, receiver_id, content, timestamp
                FROM messages
                WHERE (sender_id = %s AND receiver_id = %s) 
                   OR (sender_id = %s AND receiver_id = %s)
                ORDER BY timestamp ASC
            ''', (session['id'], chat_partner_id, chat_partner_id, session['id']))
            messages = cursor.fetchall()

        cursor.close()
        return render_template('messages.html', 
                               search_results=search_results, 
                               conversations=conversations, 
                               messages=messages, 
                               chat_partner=chat_partner, 
                               current_user={'username': session['username']})
    return redirect(url_for('login'))
@app.route('/submit_idea', methods=['GET', 'POST'])
def submit_idea():
    if 'loggedin' in session:
        if request.method == 'POST':
            # Collect form data
            startup_name = request.form['startup_name']
            founders_team = request.form['founders_team']
            problem_statement = request.form['problem_statement']
            solution_overview = request.form['solution_overview']
            target_market = request.form['target_market']
            business_model = request.form['business_model']
            revenue_streams = request.form['revenue_streams']
            market_analysis = request.form['market_analysis']
            competitors = request.form['competitors']
            financial_projections = request.form['financial_projections']
            funding_needed = request.form['funding_needed']

            # Insert into the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                INSERT INTO startup_ideas (
                    user_id, startup_name, founders_team, problem_statement, solution_overview, 
                    target_market, business_model, revenue_streams, market_analysis, competitors, 
                    financial_projections, funding_needed
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                session['id'], startup_name, founders_team, problem_statement, solution_overview, 
                target_market, business_model, revenue_streams, market_analysis, competitors, 
                financial_projections, funding_needed
            ))
            mysql.connection.commit()
            flash('Your startup idea has been submitted successfully!', 'success')
            return redirect(url_for('index'))

        # Fetch feedback and chat messages
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT feedback.comment, feedback.timestamp, users.username AS `from`
            FROM feedback
            JOIN users ON feedback.user_id = users.id
            WHERE feedback.application_id IN (
                SELECT id FROM startup_ideas WHERE user_id = %s
            )
        ''', (session['id'],))
        feedback = cursor.fetchall()

        cursor.execute('''
            SELECT content, sender, role, timestamp
            FROM chat_messages
            WHERE user_id = %s AND application_id IS NULL
            ORDER BY timestamp DESC
        ''', (session['id'],))
        chat_messages = cursor.fetchall()

        return render_template('submit_idea.html', feedback=feedback, chat_messages=chat_messages)
    
    return redirect(url_for('login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND role = "admin"', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = account['role']
            session['is_admin'] = True
            flash('Logged in successfully as admin.', 'success')
            return redirect(url_for('view_applications'))
        else:
            flash('Incorrect username/password or not an admin!', 'danger')
    return render_template('admin_login.html')

@app.route('/view_applications')
def view_applications():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if 'is_admin' in session and session['is_admin']:
            # Admin: View all applications
            cursor.execute('''
                SELECT users.username, startup_ideas.id, startup_ideas.startup_name, startup_ideas.problem_statement, 
                       startup_ideas.solution_overview, startup_ideas.target_market, startup_ideas.business_model,
                       startup_ideas.revenue_streams, startup_ideas.financial_projections, startup_ideas.funding_needed
                FROM startup_ideas
                JOIN users ON startup_ideas.user_id = users.id
            ''')
            applications = cursor.fetchall()

            # Fetch messages for each application
            for app in applications:
                cursor.execute('''
                    SELECT content, sender, role, timestamp
                    FROM chat_messages
                    WHERE application_id = %s
                    ORDER BY timestamp DESC
                ''', (app['id'],))
                app['messages'] = cursor.fetchall()

        else:
            # Regular user: View their own applications
            cursor.execute('''
                SELECT startup_ideas.*, feedback.comment AS feedback_comment, chat_messages.content AS message_content
                FROM startup_ideas
                LEFT JOIN feedback ON feedback.application_id = startup_ideas.id
                LEFT JOIN chat_messages ON chat_messages.application_id = startup_ideas.id
                WHERE startup_ideas.user_id = %s
            ''', (session['id'],))
            applications = cursor.fetchall()

            # Fetch messages for each application
            for app in applications:
                cursor.execute('''
                    SELECT content, sender, role, timestamp
                    FROM chat_messages
                    WHERE application_id = %s
                    ORDER BY timestamp DESC
                ''', (app['id'],))
                app['messages'] = cursor.fetchall()

        return render_template('view_applications.html', applications=applications)

    return redirect(url_for('login'))

@app.route('/submit_feedback/<int:application_id>', methods=['POST'])
def submit_feedback(application_id):
    if 'loggedin' in session and 'is_admin' in session and session['is_admin']:
        feedback = request.form['feedback']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO feedback (application_id, user_id, comment, timestamp) 
            VALUES (%s, %s, %s, NOW())
        ''', (application_id, session['id'], feedback))
        mysql.connection.commit()
        flash('Feedback submitted successfully!', 'success')
    else:
        flash('Unauthorized action.', 'danger')
    return redirect(url_for('view_applications'))
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.debug = True
    serve(app, host='127.0.0.1', port=5000)
