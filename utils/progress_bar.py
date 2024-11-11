import tkinter as tk
from tkinter import ttk
import math

class ModernProgressBar(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        
        # Extract custom parameters with defaults
        self.width = kwargs.pop('length', 300)
        self.height = kwargs.pop('height', 20)
        self.gradient_start = kwargs.pop('gradient_start', '#FF69B4')  # Hot pink
        self.gradient_end = kwargs.pop('gradient_end', '#4169E1')      # Royal blue
        self.border_width = kwargs.pop('border_width', 2)
        self.border_radius = kwargs.pop('border_radius', 10)
        
        # Create canvas for custom drawing
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg='#1a1a1a',  # Dark background
            highlightthickness=0,
        )
        self.canvas.pack(pady=10)
        
        # Initialize progress value
        self._progress = 0
        
        # Create the loading text
        self.loading_text = kwargs.pop('text', 'LOADING...')
        self.text_color = kwargs.pop('text_color', '#FFFFFF')
        
        # Draw initial state
        self._draw_border()
        self._draw_progress()
        
    def _create_gradient(self, width):
        """Create a gradient by generating intermediate colors"""
        gradient = []
        r1, g1, b1 = self._hex_to_rgb(self.gradient_start)
        r2, g2, b2 = self._hex_to_rgb(self.gradient_end)
        
        for i in range(width):
            ratio = i / width
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            gradient.append(f'#{r:02x}{g:02x}{b:02x}')
        return gradient
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _draw_border(self):
        """Draw the rounded border of the progress bar"""
        self.canvas.delete('border')
        x0, y0 = self.border_width, self.border_width
        x1 = self.width - self.border_width
        y1 = self.height - self.border_width
        
        # Draw rounded rectangle border
        self.canvas.create_rounded_rectangle(
            x0, y0, x1, y1,
            radius=self.border_radius,
            outline='#303030',  # Subtle border color
            width=self.border_width,
            tags='border'
        )
    
    def _draw_progress(self):
        """Draw the progress bar with gradient effect"""
        self.canvas.delete('progress', 'text')
        
        # Calculate progress width
        progress_width = int((self.width - 2 * self.border_width) * self._progress / 100)
        
        if progress_width > 0:
            # Create gradient for current progress width
            gradient = self._create_gradient(progress_width)
            
            # Draw gradient rectangles
            for i in range(progress_width):
                x0 = i + self.border_width
                y0 = self.border_width
                x1 = x0 + 1
                y1 = self.height - self.border_width
                
                self.canvas.create_line(
                    x0, y0, x0, y1,
                    fill=gradient[i],
                    width=1,
                    tags='progress'
                )
        
        # Draw loading text
        text_x = self.width / 2
        text_y = self.height / 2
        self.canvas.create_text(
            text_x, text_y,
            text=f"{self.loading_text} {int(self._progress)}%",
            fill=self.text_color,
            font=('Helvetica', 8, 'bold'),
            tags='text'
        )
    
    def set(self, value):
        """Set progress value (0-100)"""
        self._progress = min(100, max(0, value))
        self._draw_progress()
        self.update_idletasks()

# Add rounded rectangle capability to Canvas
def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]

    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle

def create_progress_bar(root, **kwargs):
    """Create and return a modern progress bar instance"""
    progress_bar = ModernProgressBar(root, **kwargs)
    progress_bar.pack(pady=20)
    return progress_bar

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#1a1a1a')  # Dark theme
    root.title("Modern Progress Bar Demo")
    
    # Create progress bar with custom colors
    pb = create_progress_bar(
        root,
        length=400,
        height=30,
        gradient_start='#FF69B4',  # Hot pink
        gradient_end='#4169E1',    # Royal blue
        text='LOADING...',
        text_color='#FFFFFF'
    )
    
    # Simulate progress
    def update_progress():
        current = 0
        def step():
            nonlocal current
            if current <= 100:
                pb.set(current)
                current += 1
                root.after(50, step)
        step()
    
    # Start progress after a short delay
    root.after(500, update_progress)
    root.mainloop()