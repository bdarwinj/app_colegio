class User:
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    def __repr__(self):
        return f"{self.username} ({self.role})"