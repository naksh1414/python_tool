import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from datetime import datetime
from aws_config import users_table

class ModernSignUp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Sign Up")
        self.root.geometry("400x600")
        self.root.configure(bg="white")
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        # Configure styles for modern look
        style = ttk.Style()
        style.configure('Modern.TEntry',
            fieldbackground='white',
            borderwidth=0,
            relief='flat',
            padding=10
        )
        
        style.configure('Modern.TFrame',
            background='white'
        )

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Header
        tk.Label(
            main_frame,
            text="Sign Up",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#1a1a1a'
        ).pack(pady=(0, 20))

        # Subtitle
        tk.Label(
            main_frame,
            text="Let's get started with our 30 days free trial",
            font=('Arial', 10),
            bg='white',
            fg='#666666'
        ).pack(pady=(0, 20))

        # Email field
        tk.Label(
            main_frame,
            text="Email",
            font=('Arial', 10),
            bg='white',
            fg='#666666',
            anchor='w'
        ).pack(fill='x')
        
        self.email_entry = ttk.Entry(
            main_frame,
            style='Modern.TEntry',
            font=('Arial', 11)
        )
        self.email_entry.pack(fill='x', pady=(5, 15))

        # Password field
        tk.Label(
            main_frame,
            text="Password",
            font=('Arial', 10),
            bg='white',
            fg='#666666',
            anchor='w'
        ).pack(fill='x')
        
        self.password_entry = ttk.Entry(
            main_frame,
            style='Modern.TEntry',
            font=('Arial', 11),
            show="•"
        )
        self.password_entry.pack(fill='x', pady=(5, 20))

        # Sign Up button
        sign_up_button = tk.Button(
            main_frame,
            text="Sign Up",
            font=('Arial', 11, 'bold'),
            bg='#1a73e8',
            fg='white',
            relief='flat',
            command=self.register_user,
            cursor='hand2'
        )
        sign_up_button.pack(fill='x', ipady=10, pady=(0, 15))

        # Login link
        login_frame = tk.Frame(main_frame, bg='white')
        login_frame.pack(fill='x')
        
        tk.Label(
            login_frame,
            text="Already have an account? ",
            font=('Arial', 10),
            bg='white',
            fg='#666666'
        ).pack(side=tk.LEFT)
        
        login_link = tk.Label(
            login_frame,
            text="Log in",
            font=('Arial', 10),
            bg='white',
            fg='#1a73e8',
            cursor='hand2'
        )
        login_link.pack(side=tk.LEFT)
        login_link.bind("<Button-1>", lambda e: self.open_login_screen())

        # Separator
        separator_frame = tk.Frame(main_frame, bg='white')
        separator_frame.pack(fill='x', pady=20)
        
        # tk.Frame(separator_frame, bg='#e0e0e0', height=1).pack(fill='x', pady=10)
        # tk.Label(
        #     separator_frame,
        #     text="or",
        #     font=('Arial', 10),
        #     bg='white',
        #     fg='#666666'
        # ).place(relx=0.5, rely=0.5, anchor='center')

        # Google Sign In button
        # google_button = tk.Button(
        #     main_frame,
        #     text="Sign up with Google",
        #     font=('Arial', 11),
        #     bg='white',
        #     fg='#666666',
        #     relief='solid',
        #     borderwidth=1,
        #     cursor='hand2'
        # )
        # google_button.pack(fill='x', ipady=10)

        # Terms and Privacy
        tk.Label(
            main_frame,
            text="By signing up, you agree to our company's Terms of Use and Privacy Policy",
            font=('Arial', 8),
            bg='white',
            fg='#666666',
            wraplength=300,
            justify='center'
        ).pack(pady=20)

    def register_user(self):
        username = self.email_entry.get()
        password = self.password_entry.get()
         # Default values for new user
        default_access_level = 'push'
        default_upload_limit = '1 GB'
        default_bucket_access = ['atool']
        default_folder_access = ['new']
        
        users_table.put_item(
            Item={
                'username': username,
                'password': password,
                'created_at': str(datetime.now()),
                'access_level': default_access_level,  # Default: push
                'upload_limit': default_upload_limit,  # Default: 1 GB
                'bucket_access': default_bucket_access,
                'folder_access': default_folder_access
            }
        )
        
        self.root.destroy()
        # Redirect to login screen
        from loginNew import login_screen
        login_screen()
        
    def open_login_screen(self):
        self.root.destroy()
        from loginNew import login_screen
        login_screen()

# Function to create the register screen (for backward compatibility)
def register_screen():
    app = ModernSignUp()
    app.run()

if __name__ == "__main__":
    app = ModernSignUp()
    app.run()