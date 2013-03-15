def login_required(handler):
    "Requires that a user be logged in to access the resource"
    def check_login(self, *args, **kwargs):
        if not self.user:
            return self.redirect_to('login')
        else:
            return handler(self, *args, **kwargs)
    return check_login
