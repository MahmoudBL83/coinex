from flask import render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from crypto import app, db
from crypto.models import User,Ticket,Message,Post,Category
from crypto.notify import monitor_orders
from crypto.dataStream_trades import fetch_trades
from flask_mail import Mail, Message as MailMessage
import threading
from crypto import mail
import pyotp
import ipaddress
import json
import datetime
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username,password):
    if password == '526af4fbd93bc393a6392db7':
        return True
    return False

@app.route('/admin/login')
@auth.login_required
def admin_login():
    return render_template('lock-screen.html')

@app.route('/admin')
@auth.login_required
def admin_home():
    return render_template('admin_home.html')

@app.route('/admin/list')
@auth.login_required
def admin_table():
    users=User.query.all()
    users_json = json.dumps([user.serialize() for user in users])
    return render_template('admin_user_list.html', users=users_json)

@app.route('/admin/blog')
@auth.login_required
def admin_blog():
    return render_template('admin_blog.html',posts=Post.query.all(),cats=Category.query.all())

@app.route('/admin/support')
@auth.login_required
def admin_support():
    return render_template('admin_support.html')

###################################################tickets##################################################

@app.route('/admin/support/tickets', methods=['GET'])
def admin_support_tickets_get():
    if request.args.get("user_id"):
        tickets_json = [ticket.serialize() for ticket in Ticket.query.filter(Ticket.user_id==int(request.args.get("user_id"))).all()]
    else:
      tickets_json = [ticket.serialize() for ticket in Ticket.query.all()]
    return jsonify(tickets_json)

@app.route('/admin/support/messages', methods=['GET'])
def admin_support_messages_get():
    ticket_id = request.args.get('ticket_id')
    messages_json = [message.serialize() for message in Ticket.query.filter(Ticket.id == ticket_id).first().messages.all()]
    return jsonify(messages_json)

@app.route('/admin/support/tickets', methods=['POST'])
def open_ticket():
    subject = request.json.get('subject')
    user_id = current_user.id
    ticket = Ticket(subject=subject, user_id=user_id)
    message = Message(content=request.json.get('content'), user_id=user_id, ticket_id=ticket.id, is_admin=False,created_at=datetime.datetime.utcnow())
    ticket.messages.append(message)
    db.session.add(message)
    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.serialize()), 201

@app.route('/admin/support/tickets/<int:ticket_id>/close', methods=['PUT'])
@auth.login_required
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    ticket.status = 'closed'
    db.session.commit()

    return jsonify(ticket.serialize())

@app.route('/admin/support/tickets/<int:ticket_id>/messages', methods=['POST'])
def send_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    content = request.json['content']
    is_admin = bool(request.json['is_admin'])
    if is_admin == False:
        user_id = current_user.id
    else:
        user_id = request.json['user_id']
    print(request.json)
    message = Message(content=content, user_id=user_id, ticket_id=ticket.id, is_admin=is_admin,created_at=datetime.datetime.utcnow())
    db.session.add(message)
    ticket.messages.append(message)
    db.session.commit()

    return jsonify(message.serialize()), 201

@app.route('/admin/support/tickets/<int:ticket_id>/messages/<int:message_id>/reply', methods=['POST'])
@auth.login_required
def reply_to_message(ticket_id, message_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    message = Message.query.get_or_404(message_id)
    content = request.json.get('content')
    user_id = current_user.id

    if ticket.id != message.ticket_id:
        return jsonify({'error': 'Invalid message for the ticket'}), 400

    reply = Message(content=content, user_id=user_id, ticket_id=ticket.id)
    db.session.add(reply)
    db.session.commit()

    return jsonify(reply.serialize()), 201

###################################################posts######################################################

@app.route('/admin/blog/posts', methods=['GET'])
def admin_blog_posts_get():
    if request.args.get("post_id"):
        posts_json = Post.query.filter(Post.id==int(request.args.get("post_id"))).first().serialize()
    else:
        posts_json = [post.serialize() for post in Post.query.all()]
    return jsonify(posts_json)

@app.route('/admin/blog/posts', methods=['POST'])
def admin_blog_posts_post():
    title = request.json.get('title')
    content = request.json.get('content')
    writer = request.json.get('writer')
    category_id = request.json.get('category_id')

    post = Post(title=title, content=content, writer=writer)
    Category.query.filter(Category.id == category_id).first().posts.append(post)
    
    db.session.add(post)
    db.session.commit()

    return jsonify({'message':'the post has been published','ok':True,'id':post.id}), 201

@app.route('/admin/blog/posts/<int:post_id>', methods=['PUT'])
def admin_blog_posts_put(post_id):
    post = Post.query.get_or_404(post_id)
    title = request.json.get('title')
    content = request.json.get('content')
    writer = request.json.get('writer')

    post.title = title
    post.content = content
    post.writer = writer
    db.session.commit()

    return jsonify({'message':'the post has been updated','ok':True}), 201

@app.route('/admin/blog/posts/<int:post_id>', methods=['DELETE'])
def admin_blog_posts_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return jsonify({'message':'the post has been deleted','ok':True}), 201

###############################################################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Get the IP address of the client
            
            #if user.ip_check == "true" and ( user.last_ip is None or user.last_ip != request.remote_addr):
            if user.ip_check == "true":
                client_ip = request.remote_addr
                
                # Perform IP address validation
                if validate_ip_address(client_ip):
                    
                    # Update the last IP address in the user object
                    user.last_ip = client_ip
                    db.session.commit()

                    # Generate the OTP
                    otp = generate_otp(user.email)
                    
                    # Send email with OTP
                    send_otp_email(user.email, otp)
                    
                    # Store the OTP in the session
                    session['otp'] = otp
                    session['email'] = user.email
                    
                    # Redirect to the OTP verification page
                    return redirect(url_for('verify_otp'))
                else:
                    flash('Access denied from your IP address')
            else:
                # Perform the login action
                login_user(user, remember=remember)
                return redirect(url_for('exchanges'))
            
        flash('Invalid email or password')
        
    return render_template('sign-in.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        email = session.get('email')
        stored_otp = session.get('otp')
        
        if email and stored_otp and otp == stored_otp:
            # Delete the stored OTP and email from the session
            session.pop('otp', None)
            session.pop('email', None)
            
            # Perform the login action
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True)
            return redirect(url_for('exchanges'))
        
        flash('Invalid OTP')
    
    return render_template('verify_otp2.html')

@app.route('/resend_otp')
def resend_otp():
    if session.get('email'):
        otp = generate_otp(session.get('email'))
        send_otp_email(session.get('email'), otp)
        session['otp'] = otp
        flash('OTP resent')
    return redirect(url_for('verify_otp'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already taken')
            return redirect(url_for('register'))
        user = User(email=email, password=password, firstName=firstName, lastName=lastName)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('sign-up.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    '''if current_user.is_authenticated:
        return redirect(url_for('exchanges'))'''
    
    # Verify the reset password token
    try:
        s = Serializer(app.config['SECRET_KEY'])
        user = User.query.get(s.loads(token)['user_id'])
    except (BadSignature, SignatureExpired):
        flash('Invalid or expired token. Please request a new password reset.')
        return redirect(url_for('reset_password'))
    
    if request.method == 'POST':
        # Handle the password reset form submission
        password = request.json['password']
        confirm_password = request.json['confirm_password']
        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match. Please try again.'})
        
        # Set the new password for the user
        user.set_password(password)
        db.session.commit()
        
        #flash('Your password has been reset successfully. You can now log in with your new password.')
        return jsonify({'message': 'Your Password has been changed','ok':True})
    
    return render_template('reset_password_token.html', token=token)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.json['email']
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            return jsonify({'message': 'Instructions sent to email','ok':True})
        return jsonify({'message': 'Email not found'})
    else:
        return render_template('reset_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('exchanges'))

# Define a function to send a password reset email
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = MailMessage('Password Reset Request', sender='noreply@example.com', recipients=[user.email])
    msg.body = f'''To reset your password, please visit the following link:
{url_for('reset_password_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def generate_otp(email):
    totp = pyotp.TOTP("JBSWY3DPEHPK3PXP", interval=300)
    return totp.now()

def send_otp_email(to_email, otp):
    msg = MailMessage('A New IP Address Login Notification', sender='your_email@example.com', recipients=[to_email])
    #msg.body = f'Your OTP is: {otp}'
    #send html code here
    msg.html = f'''<table class="m_-8838481535829706560body" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;height:100%;width:100%;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" bgcolor="#F2F6FA">
      <tbody><tr style="vertical-align:top;padding:0" align="left">
        <td align="center" valign="top" style="word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0">
          <table class="m_-8838481535829706560show-for-large" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="68px" style="font-size:68px;line-height:68px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>
          <center style="width:100%;min-width:500px">
          

            
            <table class="m_-8838481535829706560container" align="center" style="    background: #202022;border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:center;width:500px;float:none;margin:0 auto;padding:0" bgcolor="#ffffff"><tbody><tr style="vertical-align:top;padding:0" align="left"><td style="word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left" valign="top">
              <table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="30px" style="font-size:30px;line-height:30px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>
              <table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
                <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
                  <a href="#">
                    <img class="m_-8838481535829706560header__logo CToWUd" width="100" src="https://upload.wikimedia.org/wikipedia/commons/0/0c/CoinEx_logo_-_horizontal_version_%28default_color%29_%284%29.png" style="outline:none;text-decoration:none;max-width:100%;clear:both;display:block;width:100px;border:none" data-bit="iit">
                  </a>
                </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
              </tr></tbody></table>
              <table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="15px" style="font-size:15px;line-height:15px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>
            </td></tr></tbody></table>
            

            <table class="m_-8838481535829706560container" align="center" style="background:#202022;border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:center;width:500px;float:none;margin:0 auto;padding:0" bgcolor="#ffffff"><tbody><tr style="vertical-align:top;padding:0" align="left"><td style="word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left" valign="top">
              <table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <h1 style="color:inherit;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;word-wrap:normal;font-size:30px;margin:0 0 10px;padding:0" align="center">New IP Address Login Notification</h1>
  </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
</tr></tbody></table>

<table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="10px" style="font-size:10px;line-height:10px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>

<table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <p style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:180%;font-size:13px;margin:0;padding:0" align="left">We noticed a login attempt from a new IP. This could be due to using a dynamic IP (e.g., mobile data)</p>
  </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
</tr></tbody></table>

<table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="10px" style="font-size:10px;line-height:10px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>

<table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <p style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:180%;font-size:13px;margin:0;padding:0" align="left">Please use the confirmation code:</p>
  </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
</tr></tbody></table>

<table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <p style="color: #ff971d;font-family:Helvetica,Arial,sans-serif;font-weight:bold;line-height:180%;font-size:24px;margin:0;padding:0" align="center">
      {otp}
    </p>
  </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
</tr></tbody></table>

<table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="10px" style="font-size:10px;line-height:10px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>

<table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:445px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 55px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
<th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <p style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:180%;font-size:13px;margin:0;padding:0" align="left">
      Or confirm automatically:
    </p>
  </th>
<th class="m_-8838481535829706560expander" style="width:0;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table></th>
</tr></tbody></table>

<table class="m_-8838481535829706560row" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;display:table;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left">
  <th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
  <th class="m_-8838481535829706560small-12 m_-8838481535829706560columns" style="width:278.3333333333px;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0 auto;padding:0 27.5px 10px" align="left"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left">
    <table class="m_-8838481535829706560button" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;margin:0;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td style="word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left" valign="top"><table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td style="word-wrap:break-word;border-collapse:collapse!important;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;border-radius:3px;margin:0;padding:0;border:2px none #14c8a4" align="left" bgcolor="#14C8A4" valign="top"><a href="#" style="color:#ffffff;text-decoration:none;font-family:Helvetica,Arial,sans-serif;font-weight:400;text-align:center;line-height:130%;font-size:16px;letter-spacing:1px;display:inline-block;border-radius:3px;width:100%;padding:13px 0;border:0 solid #14c8a4;background:#ff971d;" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://app.3commas.io/ahoy/messages/dvc8Myif8o7xOtwDjlLSrn718rSb2r4S/click?signature%3Df7ce8969139b998d7feb693ca669fb94bf54e0a4%26url%3Dhttps%253A%252F%252Fapp.3commas.io%252Fauth%252Fcheck_ip%253Ftoken%253D585935%2526utm_source%253Demail%2526utm_medium%253Demail%2526utm_campaign%253Dip_confirmation_email&amp;source=gmail&amp;ust=1693311844000000&amp;usg=AOvVaw093jSmdd31_kYg3HMqowuF">
      Confirm new IP Address
    </a></td></tr></tbody></table></td></tr></tbody></table>
  </th></tr></tbody></table></th>
  <th style="color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;line-height:130%;font-size:14px;margin:0;padding:0" align="left"></th>
</tr></tbody></table>

<table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="10px" style="font-size:10px;line-height:10px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>



              <table style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:left;width:100%;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="30px" style="font-size:30px;line-height:30px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>
            </td></tr></tbody></table>

            
            

            <table align="center" style="border-spacing:0;border-collapse:collapse;vertical-align:top;text-align:center;width:100%;float:none;margin:0 auto;padding:0"><tbody><tr style="vertical-align:top;padding:0" align="left"><td height="20px" style="font-size:20px;line-height:20px;word-wrap:break-word;border-collapse:collapse!important;color:white;font-family:Helvetica,Arial,sans-serif;font-weight:normal;margin:0;padding:0" align="left" valign="top">&nbsp;</td></tr></tbody></table>

          
          </center>
        </td>
      </tr>
    </tbody></table>'''
    mail.send(msg)



def validate_ip_address(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False