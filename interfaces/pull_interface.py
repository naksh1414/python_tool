import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import tkinterdnd2 as tkdnd
import os
import threading
import queue
import boto3
from datetime import datetime

class ModernTheme:
    def __init__(self, root):
        self.style = ttk.Style(root)
        self.configure_theme()
        
    def configure_theme(self):
        # Configure basic colors
         self.style.configure('.',
            background='#f0f0f0',
            foreground='#333333',
            fieldbackground='white',
            troughcolor='#E0E0E0',
            font=('Roboto', 10)
        )
        
        # Configure Frame
         self.style.configure('TFrame',
            background='#f0f0f0',
            borderwidth=0
        )
        
        # Configure Label
         self.style.configure('TLabel',
            background='#f0f0f0',
            foreground='#333333',
            padding=5,
            font=('Roboto', 10)
        )
        
        # Configure Button
         self.style.configure('TButton',
            background='#4CAF50',
            foreground='white',
            padding=(10, 5),
            borderwidth=0,
            font=('Roboto', 10, 'bold')
        )
         self.style.map('TButton',
            background=[('active', '#45a049'), ('disabled', '#a5d6a7')],
            foreground=[('disabled', '#ffffff')]
        )
        
        # Configure Entry
         self.style.configure('TEntry',
            padding=8,
            relief='flat',
            borderwidth=0
        )
        
        # Configure Progressbar
         self.style.configure('TProgressbar',
            background='#4CAF50',
            troughcolor='#E0E0E0',
            borderwidth=0,
            thickness=10
        )
        
        # Configure Treeview
         self.style.configure('Treeview',
            background='white',
            fieldbackground='white',
            foreground='#333333',
            borderwidth=0,
            relief='flat',
            rowheight=30
        )
         self.style.configure('Treeview.Heading',
            background='#e0e0e0',
            foreground='#333333',
            padding=5,
            font=('Roboto', 10, 'bold')
        )
         self.style.map('Treeview',
            background=[('selected', '#4CAF50')],
            foreground=[('selected', 'white')]
        )
        
        # Configure LabelFrame
         self.style.configure('TLabelframe',
            background='white',
            borderwidth=1,
            relief='solid',
            padding=15
        )
         self.style.configure('TLabelframe.Label',
            background='white',
            foreground='#333333',
            font=('Roboto', 12, 'bold'),
            padding=(5, 5)
        )
        
        # Configure Scrollbar
         self.style.configure('TScrollbar',
            background='#f0f0f0',
            troughcolor='white',
            borderwidth=0,
            arrowsize=12
        )

class S3Helper:
    def __init__(self):
        self.s3_client = boto3.client('s3')

    def list_buckets(self):
        try:
            response = self.s3_client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
        except Exception as e:
            raise Exception(f"Failed to list buckets: {str(e)}")
    
    def list_bucket_contents(self, bucket_name, prefix=''):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except Exception as e:
            raise Exception(f"Failed to list bucket contents: {str(e)}")
        
    def upload_file(self, file_obj, s3_path, bucket_name, callback=None):
        try:
            if callback:
                # Create a wrapper for the callback that doesn't use Tkinter
                def progress_wrapper(bytes_amount):
                    try:
                        if callback:
                            callback(bytes_amount)
                    except Exception:
                        pass  # Suppress any callback errors
                
                self.s3_client.upload_fileobj(
                    file_obj,
                    bucket_name,
                    s3_path,
                    Callback=progress_wrapper
                )
            else:
                self.s3_client.upload_fileobj(
                    file_obj,
                    bucket_name,
                    s3_path
                )
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")    
    
    def upload_file(self, file_obj, s3_path, bucket_name, callback=None):
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                s3_path,
                Callback=callback
            )
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def create_folder(self, bucket_name, folder_path):
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=folder_path
            )
        except Exception as e:
            raise Exception(f"Failed to create folder: {str(e)}")
        
    def download_file(self, bucket_name, object_key, local_path, callback=None):
        try:
            file_size = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)['ContentLength']
            
            def progress_wrapper(bytes_amount):
                if callback:
                    callback(bytes_amount, file_size)
            
            self.s3_client.download_file(
                bucket_name,
                object_key,
                local_path,
                Callback=progress_wrapper
            )
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")    


class FileDownloaderApp:
    def __init__(self, username):
        self.root = tkdnd.Tk()
        self.root.configure(bg='white')  # Set root background to white
        self.theme = ModernTheme(self.root)
        self.username = username
        self.current_file = None
        self.selected_bucket = None
        self.current_folder = ""
        self.s3_helper = S3Helper()
        self.storage_limit = 1024 * 1024 * 1024  # 1GB default limit
        self.upload_history = []
        self.history_labels = []
        self.bucket_name = None 
        self.setup_window()
        self.create_widgets()
        self.update_queue = queue.Queue()
        self.process_queue()
        self.dragged_item = None
        self.drag_indicator = None
        self.last_highlight = None
        self.current_storage_usage = 0
        self.update_current_storage_usage()
        self.bucket_tree.tag_configure('drag_highlight', background='lightblue')
        self.bucket_tree.tag_configure('valid_target', background='#e0ffe0')  # Light green
        self.bucket_tree.tag_configure('invalid_target', background='#ffe0e0') 
        self.load_buckets()
        
    def close_context_menu(self, event):
        self.context_menu.unpost()    

    def setup_window(self):
        self.root.title(f"Combined S3 Interface - {self.username}")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # Set window size and position
        self.root.geometry(f"{screen_width}x{screen_height}")
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Handle different OS window states
        if os.name == 'posix':
            try:
                self.root.attributes('-zoomed', True)
            except:
                self.root.attributes('-fullscreen', True)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        
    def create_drag_indicator(self, event):
        """Create a floating window to indicate dragging"""
        if self.drag_indicator:
            self.drag_indicator.destroy()
            
        # Create a new toplevel window
        self.drag_indicator = tk.Toplevel(self.root)
        self.drag_indicator.overrideredirect(True)
        self.drag_indicator.attributes('-alpha', 0.7)  # Make it semi-transparent
        
        # Get the dragged item's text and icon
        item_text = self.bucket_tree.item(self.dragged_item)["text"]
        is_folder = self.bucket_tree.item(self.dragged_item)["values"][0] == "Folder"
        
        # Create label with icon and text
        icon = "📁" if is_folder else "📄"
        label = tk.Label(
            self.drag_indicator,
            text=f"{icon} {item_text}",
            bg='lightgray',
            padx=5,
            pady=3
        )
        label.pack()
        
        # Position the window at the cursor
        self.drag_indicator.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")        

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Create title section
        self.create_title_section(main_frame)
        
        # Create buckets section
        self.create_buckets_section(main_frame)
        
        # Create file upload section
        # self.create_file_upload_section(main_frame)
        
        # Create history section
        self.create_history_section(main_frame)

    def create_title_section(self, parent):
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="File Management System",
            font=('Segoe UI', 24, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(20, 5))

        # Storage usage display
        # self.storage_frame = ttk.Frame(title_frame)
        # self.storage_frame.grid(row=1, column=0, pady=5)
        # self.storage_label = ttk.Label(
        #     self.storage_frame,
        #     text="Storage Usage: 0/1GB"
        # )
        # self.storage_label.grid(row=0, column=0)

    def create_buckets_section(self, parent):
        buckets_frame = ttk.LabelFrame(parent, text="S3 Buckets", padding="20")
        buckets_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        buckets_frame.grid_columnconfigure(1, weight=1)

        # Create left panel for bucket list
        left_panel = ttk.Frame(buckets_frame)
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))

        # Bucket listbox
        self.bucket_listbox = tk.Listbox(           
            left_panel,
            width=30,
            height=15,
            bg='white',
            fg='black',
            selectmode='single',
            relief='flat',
            borderwidth=1,
            selectbackground='#333333',
            selectforeground='white',
            font=('Segoe UI', 10)
        )
        self.bucket_listbox.grid(row=0, column=0, sticky="ns")
        self.bucket_listbox.bind('<<ListboxSelect>>', self.on_bucket_select)

        # Scrollbar for bucket listbox
        bucket_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.bucket_listbox.yview)
        bucket_scrollbar.grid(row=0, column=1, sticky="ns")
        self.bucket_listbox.configure(yscrollcommand=bucket_scrollbar.set)

        # Refresh buckets button
        refresh_btn = ttk.Button(
            left_panel,
            text="↻ Refresh",
            command=self.load_buckets,
            style='TButton'
        )
        refresh_btn.grid(row=1, column=0, columnspan=2, pady=(10,0))

        # Create right panel for bucket contents
        right_panel = ttk.Frame(buckets_frame)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)

        # Folder management buttons
        folder_buttons_frame = ttk.Frame(right_panel)          
        folder_buttons_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        create_folder_btn = ttk.Button(
            folder_buttons_frame,
            text="+ New Folder",
            command=self.create_folder
        )
        
        create_folder_btn.grid(row=0, column=0, padx=5)
        delete_folder_btn = ttk.Button(
            folder_buttons_frame,
            text=" - Delete Folder",
            command=self.delete_folder
        )
        delete_folder_btn.grid(row=0, column=2, padx=5)

        # Add back button for navigation
        self.back_btn = ttk.Button(
            folder_buttons_frame,
            text="← Back",
            command=self.go_back
        )
        self.back_btn.grid(row=0, column=1, padx=5)
        self.back_btn.grid_remove()  # Hide initially

        # Current path label
        self.path_label = ttk.Label(right_panel, text="")
        self.path_label.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Bucket contents tree
        self.bucket_tree = ttk.Treeview(
            right_panel,
            columns=("Size",),
            show='tree headings'
        )
        self.bucket_tree.heading("Size", text="Size")
        self.bucket_tree.grid(row=2, column=0, sticky="nsew")
        self.bucket_tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Scrollbar for bucket contents
        tree_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.bucket_tree.yview)
        tree_scrollbar.grid(row=1, column=1, sticky="ns")
        self.bucket_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Bind drag and drop events
        self.bucket_tree.bind("<ButtonPress-1>", self.on_start_drag)
        self.bucket_tree.bind("<ButtonRelease-1>", self.on_drop)

        # Scrollbar for bucket tree
        tree_scrollbar = ttk.Scrollbar(
            right_panel,
            orient="vertical",
            command=self.bucket_tree.yview
        )
        tree_scrollbar.grid(row=2, column=1, sticky="ns")
        self.bucket_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Modify the bucket tree creation with right-click menu
        self.bucket_tree = ttk.Treeview(
            right_panel,
            columns=("Size",),
            show='tree headings'
        )
        self.bucket_tree.heading("Size", text="Size")
        self.bucket_tree.grid(row=2, column=0, sticky="nsew")
        
        # self.context_menu.config(
        #     bg="white",        # Menu background
        #     fg="black",        # Menu text color
        #     activebackground="#333333",  # Hovered menu item background
        #     activeforeground="white"     # Hovered menu item text color
        # )
        # Create right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0,activebackground="#333333",  activeforeground="white")
        # self.context_menu.add_command(label="Delete", command=self.delete_selected_item , accelerator="CTRL + D",font=('Segoe UI', 10))   
        self.context_menu.add_command(label="Download", command=self.download_selected_item ,font=('Segoe UI', 10))
        
        # Bind events
        self.bucket_tree.bind("<Double-1>", self.on_tree_double_click)
        self.bucket_tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.bucket_tree.bind("<ButtonPress-1>", self.on_start_drag)
        self.bucket_tree.bind("<B1-Motion>", self.on_drag)
        self.bucket_tree.bind("<ButtonRelease-1>", self.on_drop)
        self.root.bind("<Button-1>", self.close_context_menu)

    def load_buckets(self):
        """Load and display available S3 buckets"""
        try:
            self.bucket_listbox.delete(0, tk.END)
            buckets = self.s3_helper.list_buckets()
            for bucket in buckets:
                self.bucket_listbox.insert(tk.END, bucket)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load buckets: {str(e)}")
            
            
    def update_current_storage_usage(self):
        """Update the current storage usage value"""
        try:
            self.current_storage_usage = self.get_current_storage_usage()
            self.update_storage_display()
        except Exception as e:
            print(f"Error updating storage usage: {str(e)}")        
            
    def on_bucket_select(self, event):
        """Handle bucket selection"""
        selection = self.bucket_listbox.curselection()
        if selection:
            self.selected_bucket = self.bucket_listbox.get(selection[0])
            self.current_folder = ""  # Reset current folder
            self.refresh_bucket_contents()  # Ensure bucket contents are loaded
            self.update_path_label()        
            

    def create_file_upload_section(self, parent):
        upload_frame = ttk.LabelFrame(parent, text="File Upload", padding="20")
        upload_frame.grid(row=2, column=0, sticky="ew", pady=10)

        # File selection
        self.file_label = ttk.Label(upload_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, padx=10)

        select_file_btn = ttk.Button(
            upload_frame,
            text="Select File",
            command=self.select_file
        )
        select_file_btn.grid(row=0, column=1, padx=10)

        upload_btn = ttk.Button(
            upload_frame,
            text="Upload",
            command=self.upload_file
        )
        upload_btn.grid(row=0, column=2, padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            upload_frame,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        
        # Status label
        self.status_label = ttk.Label(upload_frame, text="")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)

    def create_history_section(self, parent):
        history_frame = ttk.LabelFrame(parent, text="Upload History", padding="20")
        history_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self.history_frame = ttk.Frame(history_frame)
        self.history_frame.grid(row=0, column=0, sticky="ew")
        
    def delete_folder(self):
        if not self.selected_bucket:
            messagebox.showerror("Error", "Please select a bucket first")
            return

        # Ensure we are selecting a folder to delete
        selected_items = self.bucket_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No folder selected")
            return

        # Get the selected folder
        selected_item = selected_items[0]
        item_text = self.bucket_tree.item(selected_item)["text"]
        values = self.bucket_tree.item(selected_item)["values"]

        # Check if it's a folder (folders in S3 usually have "/" at the end of their name)
        if not values or values[0] != "Folder":
            messagebox.showerror("Error", "Selected item is not a folder")
            return

        folder_to_delete = f"{self.current_folder}{item_text}/"

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the folder '{folder_to_delete}' and all its contents?")
        if not confirm:
            return

        # Perform the delete operation
        try:
            objects_to_delete = self.s3_helper.list_bucket_contents(self.selected_bucket, folder_to_delete)
            if not objects_to_delete:
                messagebox.showinfo("Info", "Folder is already empty")
                return

            # Delete all objects in the folder
            delete_objects = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete]}
            self.s3_helper.s3_client.delete_objects(Bucket=self.selected_bucket, Delete=delete_objects)

            messagebox.showinfo("Success", f"Folder '{folder_to_delete}' deleted successfully")
            self.refresh_bucket_contents()  # Refresh the bucket contents after deletion
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete folder: {str(e)}")
        

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))

    def create_folder(self):
        if not self.selected_bucket:
            messagebox.showerror("Error", "Please select a bucket first")
            return

        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            folder_path = (
                f"{self.current_folder}{folder_name}/"
                if self.current_folder
                else f"{folder_name}/"
            )
            try:
                self.s3_helper.create_folder(self.selected_bucket, folder_path)
                self.refresh_bucket_contents()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {str(e)}")
                
    def on_tree_double_click(self, event):
        """Handle double click on tree items"""
        selected_items = self.bucket_tree.selection()
        
        if not selected_items:
            print("No item selected.")
            return  # Exit if no item is selected

        item = selected_items[0]
        item_text = self.bucket_tree.item(item)["text"]
        values = self.bucket_tree.item(item)["values"]

        if values and values[0] == "Folder":
            # Update current folder and refresh contents
            self.current_folder += f"{item_text}/"
            self.refresh_bucket_contents()
            self.update_path_label()
            self.back_btn.grid()  # Show back button when in a folder


    def go_back(self):
        """Navigate to parent folder"""
        if self.current_folder:
            # Remove last folder from path
            folders = self.current_folder.split("/")[:-2]
            self.current_folder = "/".join(folders) + "/" if folders else ""
            self.refresh_bucket_contents()
            self.update_path_label()
            
            # Hide back button if we're at root
            if not self.current_folder:
                self.back_btn.grid_remove()

    def update_path_label(self):
        """Update the current path display"""
        if self.selected_bucket:
            path = f"Bucket: {self.selected_bucket}"
            if self.current_folder:
                path += f" / {self.current_folder}"
            self.path_label.config(text=path)
        else:
            self.path_label.config(text="")                

    def on_bucket_select(self, event):
        """Handle bucket selection and change the color of the selected bucket."""
        # First, clear the highlight from all items
        for i in range(self.bucket_listbox.size()):
            self.bucket_listbox.itemconfig(i, bg="white", fg="black")  # Reset all to default colors

        # Highlight the selected item
        selection = self.bucket_listbox.curselection()
        if selection:
            self.selected_bucket = self.bucket_listbox.get(selection[0])
            self.bucket_listbox.itemconfig(selection[0], bg="lightblue", fg="white")  # Highlight with a different color

            # Reset folder and load bucket contents
            self.current_folder = ""  # Reset current folder
            self.refresh_bucket_contents()  # Ensure bucket contents are loaded
            self.update_path_label()  # Show the current path in the label


    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def get_current_storage_usage(self):
        """Calculate total storage usage for the current bucket"""
        try:
            if not self.selected_bucket:
                return 0
                
            total_size = 0
            paginator = self.s3_helper.s3_client.get_paginator('list_objects_v2')
            
            # List all objects in the bucket (not just current folder)
            pages = paginator.paginate(Bucket=self.selected_bucket)
            
            for page in pages:
                for obj in page.get('Contents', []):
                    size = obj.get('Size', 0)
                    if isinstance(size, str):
                        # Convert string sizes (like "124.00 B") to bytes
                        try:
                            if 'KB' in size:
                                size = float(size.replace(' KB', '')) * 1024
                            elif 'MB' in size:
                                size = float(size.replace(' MB', '')) * 1024 * 1024
                            elif 'GB' in size:
                                size = float(size.replace(' GB', '')) * 1024 * 1024 * 1024
                            elif 'B' in size:
                                size = float(size.replace(' B', ''))
                        except ValueError:
                            size = 0
                    total_size += size
                    
            return total_size
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get storage usage: {str(e)}")
            return 0

    
    def update_storage_display(self):
        """Update the storage usage display"""
        try:
            usage = self.get_current_storage_usage()
            usage_gb = usage / (1024 * 1024 * 1024)  # Convert bytes to GB
            limit_gb = self.storage_limit / (1024 * 1024 * 1024)
            
            # Format with proper precision
            self.storage_label.config(
                text=f"Storage Usage: {usage_gb:.2f}/{limit_gb:.2f}GB"
            )
        except Exception as e:
            print(f"Error updating storage display: {str(e)}")
            
    def refresh_bucket_contents(self):
        if self.selected_bucket:
            # Clear existing items
            for item in self.bucket_tree.get_children():
                self.bucket_tree.delete(item)
            
            # Fetch and display objects in the bucket
            self.show_bucket_objects(self.selected_bucket)
            self.update_storage_display()  # Update storage usage


    def show_bucket_objects(self, bucket_name):
        try:
            # Get the objects from the bucket
            objects = self.s3_helper.list_bucket_contents(
                bucket_name,
                prefix=self.current_folder
            )
            
            if objects:
                folder_structure = {}
                
                for obj in objects:
                    path = obj['Key']
                    size = self.format_size(obj.get('Size', 0))
                    
                    # Skip the current folder itself
                    if path == self.current_folder:
                        continue

                    # Remove the current folder prefix from the path
                    if self.current_folder:
                        path = path[len(self.current_folder):]

                    parts = path.split('/')
                    if path.endswith('/'):
                        # It's a folder
                        folder_name = parts[0]
                        if folder_name not in folder_structure:
                            self.bucket_tree.insert(
                                "",
                                "end",
                                folder_name,
                                text=folder_name,
                                values=("Folder",)
                            )
                            folder_structure[folder_name] = True
                    else:
                        # It's a file
                        if len(parts) == 1:
                            self.bucket_tree.insert(
                                "",
                                "end",
                                path,
                                text=path,
                                values=(size,)
                            )
            else:
                self.bucket_tree.insert("", "end", text="Empty folder")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve bucket objects: {str(e)}")
    def move_s3_object(self, source_key, target_key):
        """
        Logic to move an object within an S3 bucket.
        :param source_key: the S3 key (path) of the object being moved
        :param target_key: the S3 key (path) of the destination folder/object
        """
        print(f"Moving {source_key} to {target_key}")
        try:
            # Example of moving the S3 object using boto3
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=target_key)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=source_key)
            print(f"Successfully moved {source_key} to {target_key}")
        except Exception as e:
            print(f"Error moving object: {e}")


    def upload_file(self):
        if not self.current_file or not self.selected_bucket:
            messagebox.showerror("Error", "No file or bucket selected")
            return

        file_size = os.path.getsize(self.current_file)
        current_usage = self.get_current_storage_usage()
        
        if current_usage + file_size > self.storage_limit:
            messagebox.showerror("Error", "Storage limit exceeded")
            return

        self.progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.progress_bar['value'] = 0
        self.status_label.config(text="Uploading...")

        # Create and start upload thread
        upload_thread = threading.Thread(target=self.perform_upload)
        upload_thread.daemon = True
        upload_thread.start()

    def perform_upload(self):
        try:
            file_name = os.path.basename(self.current_file)
            s3_path = (
                f"{self.current_folder}{file_name}"
                if self.current_folder
                else file_name
            )
            
            file_size = os.path.getsize(self.current_file)
            uploaded_bytes = 0

            def progress_callback(bytes_uploaded):
                nonlocal uploaded_bytes
                uploaded_bytes = bytes_uploaded
                progress = (bytes_uploaded / file_size) * 100
                # Use queue instead of direct Tkinter calls
                self.update_queue.put(('progress', progress))
            
            if self.current_storage_usage + file_size > self.storage_limit:
                self.update_queue.put(('error', "Storage limit would be exceeded"))
                return
                
            with open(self.current_file, "rb") as file_obj:
                self.s3_helper.upload_file(
                    file_obj,
                    s3_path,
                    self.selected_bucket,
                    callback=progress_callback
                )
            # Use queue for success message
            self.current_storage_usage += file_size
            self.update_queue.put(('storage_update', self.current_storage_usage))
            self.update_queue.put(('success', file_name))
            self.update_queue.put(('refresh_storage', None))
        except Exception as e:
            # Use queue for error message
            self.update_queue.put(('error', str(e)))

    def update_progress(self, bytes_transferred, file_size):
        """Update progress bar (called from main thread only)"""
        progress = (bytes_transferred / file_size) * 100
        self.progress_bar['value'] = progress
        self.root.update_idletasks()
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.bucket_tree.identify_row(event.y)
        if item:
            self.bucket_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def delete_selected_item(self):
        """Delete the selected file or folder"""
        selected_items = self.bucket_tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        item_text = self.bucket_tree.item(item)["text"]
        values = self.bucket_tree.item(item)["values"]

        # Construct full path
        full_path = f"{self.current_folder}{item_text}"
        if values and values[0] == "Folder":
            full_path += "/"

        # Confirm deletion
        msg = f"Are you sure you want to delete {'folder' if values and values[0] == 'Folder' else 'file'}: {item_text}?"
        if not messagebox.askyesno("Confirm Delete", msg):
            return

        try:
            if values and values[0] == "Folder":
                # Delete folder and its contents
                objects = self.s3_helper.list_bucket_contents(self.selected_bucket, full_path)
                if objects:
                    delete_objects = {'Objects': [{'Key': obj['Key']} for obj in objects]}
                    self.s3_helper.s3_client.delete_objects(
                        Bucket=self.selected_bucket,
                        Delete=delete_objects
                    )
            else:
                # Delete single file
                self.s3_helper.s3_client.delete_object(
                    Bucket=self.selected_bucket,
                    Key=full_path
                )

            messagebox.showinfo("Success", f"Successfully deleted {item_text}")
            self.refresh_bucket_contents()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {str(e)}")   
                     
    def download_selected_item(self):
        """Download the selected file or folder"""
        selected_items = self.bucket_tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        item_text = self.bucket_tree.item(item)["text"]
        values = self.bucket_tree.item(item)["values"]

        # Don't allow downloading folders directly
        if values and values[0] == "Folder":
            messagebox.showerror("Error", "Cannot download folders directly. Please download individual files.")
            return

        # Construct full path
        full_path = f"{self.current_folder}{item_text}"

        # Ask user for download location
        download_path = filedialog.asksaveasfilename(
            initialfile=item_text,
            defaultextension=".*",
            title="Save As"
        )
        
        if not download_path:
            return

        self.progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.progress_bar['value'] = 0
        self.status_label.config(text="Downloading...")

        # Create and start download thread
        download_thread = threading.Thread(
            target=self.perform_download,
            args=(full_path, download_path)
        )
        download_thread.daemon = True
        download_thread.start()  
    def perform_download(self, s3_path, local_path):
        try:
            def progress_callback(bytes_downloaded, total_bytes):
                progress = (bytes_downloaded / total_bytes) * 100
                self.update_queue.put(('progress', progress))

            self.s3_helper.download_file(
                self.selected_bucket,
                s3_path,
                local_path,
                callback=progress_callback
            )
            
            self.update_queue.put(('download_success', os.path.basename(local_path)))
        except Exception as e:
            self.update_queue.put(('error', str(e)))   
                  
    def delete_folder(self):
        if not self.selected_bucket:
            messagebox.showerror("Error", "Please select a bucket first")
            return

        # Ensure we are selecting a folder to delete
        selected_items = self.bucket_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No folder selected")
            return

        # Get the selected folder
        selected_item = selected_items[0]
        item_text = self.bucket_tree.item(selected_item)["text"]
        values = self.bucket_tree.item(selected_item)["values"]

        # Check if it's a folder (folders in S3 usually have "/" at the end of their name)
        if not values or values[0] != "Folder":
            messagebox.showerror("Error", "Selected item is not a folder")
            return

        folder_to_delete = f"{self.current_folder}{item_text}/"

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the folder '{folder_to_delete}' and all its contents?")
        if not confirm:
            return

        # Perform the delete operation
        try:
            objects_to_delete = self.s3_helper.list_bucket_contents(self.selected_bucket, folder_to_delete)
            if not objects_to_delete:
                messagebox.showinfo("Info", "Folder is already empty")
                return

            # Delete all objects in the folder
            delete_objects = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete]}
            self.s3_helper.s3_client.delete_objects(Bucket=self.selected_bucket, Delete=delete_objects)

            messagebox.showinfo("Success", f"Folder '{folder_to_delete}' deleted successfully")
            self.refresh_bucket_contents()  # Refresh the bucket contents after deletion
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete folder: {str(e)}")    
    def on_start_drag(self, event):
        """Handle the start of drag operation"""
        item = self.bucket_tree.identify_row(event.y)
        if item:
            self.dragged_item = item
            self.bucket_tree.selection_set(item)
            # Initialize drag visual feedback
            self.last_highlight = None
            self.create_drag_indicator(event)
    def on_drag(self, event):
        """Handle drag motion with visual feedback"""
        if not self.dragged_item:
            return
            
        # Create or move the drag indicator
        if not self.drag_indicator:
            self.create_drag_indicator(event)
        else:
            self.drag_indicator.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
        # Get the item under the cursor
        target_item = self.bucket_tree.identify_row(event.y)
        
        # Remove previous highlight
        if self.last_highlight and self.last_highlight != self.dragged_item:
            self.bucket_tree.item(self.last_highlight, tags=[])
            
        # Add highlight to current target if it's valid
        if target_item and target_item != self.dragged_item:
            target_values = self.bucket_tree.item(target_item)["values"]
            
            # Check if target is a folder
            if target_values and target_values[0] == "Folder":
                self.bucket_tree.item(target_item, tags=['valid_target'])
            else:
                self.bucket_tree.item(target_item, tags=['invalid_target'])
                
            self.last_highlight = target_item
            
        # Highlight the dragged item
        self.bucket_tree.item(self.dragged_item, tags=['drag_highlight'])
        
        # Auto-scroll the tree if near the edges
        tree_height = self.bucket_tree.winfo_height()
        if event.y < 20:  # Near top
            self.bucket_tree.yview_scroll(-1, 'units')
        elif event.y > tree_height - 20:  # Near bottom
            self.bucket_tree.yview_scroll(1, 'units')            

    def on_drop(self, event):
        """Handle the drop operation"""
        try:
            # Clean up drag indicator if it exists
            if self.drag_indicator:
                self.drag_indicator.destroy()
                self.drag_indicator = None
                
            # Clear highlight from last highlighted item
            if self.last_highlight:
                try:
                    if self.bucket_tree.exists(self.last_highlight):
                        self.bucket_tree.item(self.last_highlight, tags=[])
                except:
                    pass  # Ignore if item doesn't exist
                self.last_highlight = None
                
            # Clear highlight from dragged item
            if self.dragged_item:
                try:
                    if self.bucket_tree.exists(self.dragged_item):
                        self.bucket_tree.item(self.dragged_item, tags=[])
                except:
                    pass  # Ignore if item doesn't exist
                
            if not self.dragged_item:
                return

            target_item = self.bucket_tree.identify_row(event.y)
            if not target_item or target_item == self.dragged_item:
                return

            # Verify both source and target items still exist
            if not self.bucket_tree.exists(self.dragged_item) or not self.bucket_tree.exists(target_item):
                messagebox.showerror("Error", "Source or target item no longer exists")
                return

            # Get source and target information
            source_text = self.bucket_tree.item(self.dragged_item)["text"]
            source_values = self.bucket_tree.item(self.dragged_item)["values"]
            target_text = self.bucket_tree.item(target_item)["text"]
            target_values = self.bucket_tree.item(target_item)["values"]

            # Only allow dropping into folders
            if not target_values or target_values[0] != "Folder":
                messagebox.showerror("Error", "Can only drop items into folders")
                return

            # Construct source and target paths
            source_path = f"{self.current_folder}{source_text}"
            if source_values and source_values[0] == "Folder":
                source_path += "/"
                
            target_path = f"{self.current_folder}{target_text}/{source_text}"
            if source_values and source_values[0] == "Folder":
                target_path += "/"

            try:
                # Copy object to new location
                copy_source = {'Bucket': self.selected_bucket, 'Key': source_path}
                self.s3_helper.s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=self.selected_bucket,
                    Key=target_path
                )

                # Delete original object
                self.s3_helper.s3_client.delete_object(
                    Bucket=self.selected_bucket,
                    Key=source_path
                )

                # If it's a folder, move all contents
                if source_values and source_values[0] == "Folder":
                    objects = self.s3_helper.list_bucket_contents(self.selected_bucket, source_path)
                    for obj in objects:
                        old_key = obj['Key']
                        new_key = old_key.replace(source_path, target_path, 1)
                        
                        # Copy object to new location
                        copy_source = {'Bucket': self.selected_bucket, 'Key': old_key}
                        self.s3_helper.s3_client.copy_object(
                            CopySource=copy_source,
                            Bucket=self.selected_bucket,
                            Key=new_key
                        )
                        
                        # Delete original object
                        self.s3_helper.s3_client.delete_object(
                            Bucket=self.selected_bucket,
                            Key=old_key
                        )

                messagebox.showinfo("Success", f"Successfully moved {source_text}")
                self.refresh_bucket_contents()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move item: {str(e)}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during drop operation: {str(e)}")
        finally:
            self.dragged_item = None
    

    def process_queue(self):
        """Process messages from the upload thread"""
        try:
            while True:
                msg_type, msg_value = self.update_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_bar['value'] = msg_value
                    
                elif msg_type == 'download_success':
                    self.status_label.config(text="Download Successful")
                    self.progress_bar.grid_remove()
                    messagebox.showinfo("Success", f"Successfully downloaded {msg_value}")    
                    
                elif msg_type == 'storage_update':
                    self.current_storage_usage = msg_value
                    self.update_storage_display()
                    
                elif msg_type == 'success':
                    self.status_label.config(text="Upload Successful")
                    self.progress_bar.grid_remove()
                    
                    # Add to upload history
                    new_label = ttk.Label(
                        self.history_frame,
                        text=f"Uploaded: {msg_value} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    new_label.grid(sticky="w")
                    self.history_labels.append(new_label)
                    self.upload_history.append(msg_value)
                    
                    # Refresh displays
                    self.refresh_bucket_contents()
                    self.update_storage_display()
                    
                elif msg_type == 'error':
                    self.status_label.config(text="Upload Failed")
                    self.progress_bar.grid_remove()
                    messagebox.showerror("Error", msg_value)
                
        except queue.Empty:
            pass
        finally:
            # Schedule the next queue check
            self.root.after(100, self.process_queue)

    def show_success(self, file_name):
        self.status_label.config(text="Upload Successful")
        new_label = ttk.Label(
            self.history_frame,
            text=f"Uploaded: {file_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        new_label.grid(sticky="w")
        self.history_labels.append(new_label)
        self.upload_history.append(file_name)
        self.refresh_bucket_contents()
        self.root.after(0, self.update_storage_display)

    def show_error(self, error_message):
        self.status_label.config(text="Upload Failed")
        messagebox.showerror("Error", error_message)

    def run(self):
         self.root.mainloop()
         
         
