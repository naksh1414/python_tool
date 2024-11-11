# import tkinter as tk
# from tkinter import font
# from aws_config import users_table  # Ensure this is correctly set up
# from interfaces.push_interface import FileUploaderApp 
# from interfaces.pull_interface import FileDownloaderApp  
# from interfaces.both_interface import show_both_interface 
# from register import register_screen  # Ensure this function exists

# # Login Screen
# def login_screen():
#     def authenticate_user():
#         username = username_entry.get()
#         password = password_entry.get()

#         response = users_table.get_item(Key={'username': username})

#         if 'Item' in response and response['Item']['password'] == password:
#             user_type = response['Item']['user_type']
#             root.destroy()  # Close login window
#             if user_type == 'Push':
#                 FileUploaderApp(username)
#             elif user_type == 'Pull':
#                 FileDownloaderApp(username)
#             else:
#                 show_both_interface(username)
#         else:
#             error_label.config(text="Invalid credentials", fg="red")

#     def open_registration(event=None):
#         root.destroy()  # Close login window
#         register_screen()  # Open registration screen

#     root = tk.Tk()
#     root.title("Login")

#     # Set window size
#     root.geometry("500x600")
#     root.configure(bg="#1d2671")  # Dark blue-purple background

#     # Create a frame for the login form in the center
#     form_frame = tk.Frame(root, bg="white", bd=0, relief="solid")
#     form_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=400)

#     # Custom fonts
#     header_font = font.Font(family="Helvetica", size=20, weight="bold")
#     label_font = font.Font(family="Helvetica", size=12)
#     entry_font = font.Font(family="Helvetica", size=10)

#     # Header text
#     tk.Label(form_frame, text="Login", font=header_font, fg="black", bg="white").pack(pady=20)

#     # Username label and entry
#     tk.Label(form_frame, text="Email", font=label_font, fg="black", bg="white").pack(pady=5)
#     username_entry = tk.Entry(form_frame, font=entry_font, bd=1, relief="solid", width=30)
#     username_entry.pack(pady=5)

#     # Password label and entry
#     tk.Label(form_frame, text="Password", font=label_font, fg="black", bg="white").pack(pady=5)
#     password_entry = tk.Entry(form_frame, font=entry_font, bd=1, relief="solid", show="*", width=30)
#     password_entry.pack(pady=5)

#     # Error label
#     error_label = tk.Label(form_frame, text="", font=label_font, fg="red", bg="white")
#     error_label.pack()

#     # Login button
#     tk.Button(form_frame, text="Login", font=label_font, bg="#6a11cb", fg="white", width=20, height=2, relief="flat", command=authenticate_user).pack(pady=20)

#     # Forgot Password and Signup links
#     tk.Label(form_frame, text="Forgot Password?", font=entry_font, fg="grey", bg="white").pack()

#     # Make the Sign up label clickable
#     signup_label = tk.Label(form_frame, text="Don't have an account? Sign up", font=entry_font, fg="blue", bg="white", cursor="hand2")
#     signup_label.pack(pady=10)
#     signup_label.bind("<Button-1>", open_registration)

#     # Bind Esc key to exit
#     root.bind("<Escape>", lambda event: root.destroy())

#     root.mainloop()

# # To run the login screen
# if __name__ == "__main__":
#     login_screen()