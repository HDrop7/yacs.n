from db.user import User as UserModel
from db.session import Session as SessionModel
import view.message as msg
from common import *
from api_models import *


def get_user_info(session_id):
    users = UserModel()
    sessions = SessionModel()

    session = sessions.get_session(session_id)
    if session is None or len(session) == 0:
        return msg.error_msg("Unable to find the session.")

    (sessionid, uid, start_time, end_time) = session[0].values()

    if end_time is not None:
        return msg.error_msg("This session already canceled.")

    user = users.get_user(uid=uid)

    if len(user) == 0:
        return msg.error_msg("Unable to find the user")

    (uid, name, email, phone, password, major, degree, enable, _, _) = user[0].values()

    return msg.success_msg({"uid": uid, "name": name, "email": email, "phone": phone, "major": major, "degree": degree})


def update_user(user:updateUser):
    users = UserModel()
    sessions = SessionModel()

    name = user.name
    session_id = user.sessionID
    email = user.email
    phone = user.phone
    new_password = user.newPassword
    major = user.major
    degree = user.degree

    if(name==None or session_id==None or email==None or phone==None or new_password==None or major==None or degree==None):
        return msg.error_msg("Please check your requests.")

    if new_password.strip() == "":
        return msg.error_msg("Password cannot be empty.")

    if len(name) > 255:
        return msg.error_msg("Username cannot exceed 255 characters.")

    if len(new_password) > 255:
        return msg.error_msg("Password cannot exceed 255 characters.")

    # Get User according to sessionID
    session = sessions.get_session(session_id)
    if len(session) == 0:
        return msg.error_msg("Unable to find the session.")

    (sessionid, uid, start_time, end_time) = session[0].values()

    if end_time is not None:
        return msg.error_msg("This session already canceled.")

    args = {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Password": encrypt(new_password),
        "Major": major,
        "Degree": degree,
        "UID": uid
    }
    ret = users.update_user(args)

    if ret is None:
        return msg.error_msg("Failed to update user profile.")

    return msg.success_msg({})


def delete_user(form):
    users = UserModel()
    sessions = SessionModel()

    if not assert_keys_in_form_exist(form, ['sessionID', 'password']):
        return msg.error_msg("Please check the inputs.")

    password = form['password']
    session_id = form['sessionID']

    # Get User according to sessionID
    session = sessions.get_session(session_id)

    if len(session) == 0:
        return msg.error_msg("Unable to find the session.")

    (sessionid, uid, start_time, end_time) = session[0].values()

    if end_time is not None:
        return msg.error_msg("Expired SessionID")

    # Verify password
    if password.strip() == "":
        return msg.error_msg("Password cannot be empty.")

    findUser = users.get_user(uid=uid, password=encrypt(password), enable=True)
    if findUser is None:
        return msg.error_msg("Failed to find user.")

    if len(findUser) == 0:
        return msg.error_msg("Wrong password.")

    # Delete User
    ret = users.delete_user(uid)

    if ret is None:
        return msg.error_msg("Failed to delete user.")

    # Revoke all sessions
    sessions.end_session(uid=uid)

    return msg.success_msg({"uid": uid, "sessionID": session_id})


def add_user(form):
    users = UserModel()

    if not assert_keys_in_form_exist(form, ['name', 'email', 'phone', 'password', 'major', 'degree']):
        return msg.error_msg("Please check your requests.")

    name = form['name']
    email = form['email']
    phone = form['phone']
    password = form['password']
    major = form['major']
    degree = form['degree']

    if name.strip() == "":
        return msg.error_msg("Username cannot be empty.")

    if password.strip() == "":
        return msg.error_msg("Password cannot be empty.")

    if len(password) < 6:
        return msg.error_msg("Password cannot less than 6 character.")

    if len(name) > 255:
        return msg.error_msg("Username cannot exceed 255 characters.")

    if len(password) > 255:
        return msg.error_msg("Password cannot exceed 255 characters.")

    findUser = users.get_user(email=email, enable=True)

    if findUser is None:
        return msg.error_msg("Failed to find user.")

    if len(findUser) != 0:
        return msg.error_msg("User already exists. (Email already in use)")

    args = {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Password": encrypt(password),
        "Major": major,
        "Degree": degree,
        "Enable": True
    }
    res = users.add_user(args)
    if res is None:
        return msg.error_msg("Failed to add user.")

    return msg.success_msg({"msg": "User added successfully."})

def check_email(form):
    if not assert_keys_in_form_exist(form, ['email']):
        return msg.error_msg("Email required.")
    
    email = form['email']
    users = UserModel()
    
    try:
        findUser = users.get_user(email=email, enable=True)
        
        if findUser is None:
            return msg.error_msg("Failed to find user.")
        
        exists = len(findUser) > 0
        return msg.success_msg({"exists": exists})
    
    except Exception as e:
        return msg.error_msg(f"Error checking email: {str(e)}")
