from tkinter import messagebox
import tkinter as tk
from frontend import MedicalAssistantGUI


def main():
    """Main entry point"""
    
    # API Key - Replace with your actual key
    API_KEY = "AIzaSyC-q-B11SqvtmMVmYTS_qcCVS2kAzlPq9s"
    
    if API_KEY == "your-google-ai-api-key-here":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("API Key Required", 
                           "Please update the API_KEY variable in the code with your actual Google AI API key!")
        return
    
    # Create main window
    root = tk.Tk()
    app = MedicalAssistantGUI(root, API_KEY)
    root.mainloop()


if __name__ == "__main__":
    main()