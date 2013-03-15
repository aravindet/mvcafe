from models import User

webapp2_sessions = {
    'secret_key': 'not-so-secret-key'
}

webapp2_auth = {
    'user_model': User
}
