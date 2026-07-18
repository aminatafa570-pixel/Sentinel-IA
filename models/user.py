class User:
    
    def __init__(self, user_id, username, role, country):

        self.user_id = user_id
        self.username = username
        self.role = role
        self.country = country


    def display_information(self):

        print("===== USER INFORMATION =====")
        print("ID :", self.user_id)
        print("Username :", self.username)
        print("Role :", self.role)
        print("Country :", self.country)

