import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from datetime import datetime
from MedicalAssitant import MedicalAssistantAgent


class MedicalAssistantGUI:
    """Tkinter GUI for Medical Assistant Agent"""
    
    def __init__(self, root, api_key: str):
        self.root = root
        self.root.title("Medical Assistant AI")
        self.root.geometry("1100x750")
        
        # Initialize agent
        self.agent = MedicalAssistantAgent(api_key=api_key)
        
        # Current session variables
        self.current_patient_id = None
        self.current_conversation_id = None
        
        # Add menu bar
        self.create_menu()
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)  # Give more weight to right side
        main_frame.rowconfigure(0, weight=1)
        
        # Left Panel - Patient Management
        left_frame = ttk.LabelFrame(main_frame, text="Patient Management", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Patient selection
        ttk.Label(left_frame, text="Select Patient:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.patient_listbox = tk.Listbox(left_frame, height=8, width=30)  # Reduced height
        self.patient_listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.patient_listbox.bind('<<ListboxSelect>>', self.on_patient_select)
        
        # Buttons for patient management
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="New Patient", command=self.open_new_patient_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_patient_list).pack(side=tk.LEFT, padx=2)
        
        # Patient info display
        ttk.Label(left_frame, text="Patient Info:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.patient_info_text = scrolledtext.ScrolledText(left_frame, height=12, width=30, wrap=tk.WORD)  # Reduced height
        self.patient_info_text.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.patient_info_text.config(state=tk.DISABLED)
        
        # Start consultation button
        self.start_consultation_btn = ttk.Button(left_frame, text="Start New Consultation", 
                                                command=self.start_consultation, state=tk.DISABLED)
        self.start_consultation_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Right Panel Container
        right_container = ttk.Frame(main_frame)
        right_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)
        
        # Right Panel - Chat Interface
        chat_frame = ttk.LabelFrame(right_container, text="Consultation", padding="10")
        chat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=20)  # Reduced height
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="green", font=("Arial", 10))
        self.chat_display.tag_config("system", foreground="gray", font=("Arial", 9, "italic"))
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        ttk.Label(input_frame, text="Your message:").grid(row=0, column=0, sticky=tk.W)
        
        self.message_input = scrolledtext.ScrolledText(input_frame, height=3, wrap=tk.WORD)  # Reduced height
        self.message_input.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.send_btn = ttk.Button(input_frame, text="Send Message", command=self.send_message, state=tk.DISABLED)
        self.send_btn.grid(row=2, column=0, pady=5)
        
        # Bottom Panel - Consultation Summary (ALWAYS VISIBLE)
        summary_frame = ttk.LabelFrame(right_container, text="End Consultation", padding="10")
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        summary_frame.columnconfigure(1, weight=1)
        
        ttk.Label(summary_frame, text="Summary:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.summary_entry = ttk.Entry(summary_frame)
        self.summary_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(summary_frame, text="Symptoms:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.symptoms_entry = ttk.Entry(summary_frame)
        self.symptoms_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(summary_frame, text="Diagnoses:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.diagnoses_entry = ttk.Entry(summary_frame)
        self.diagnoses_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        self.end_consultation_btn = ttk.Button(summary_frame, text="📋 End Consultation", 
                                            command=self.end_consultation, state=tk.DISABLED)
        self.end_consultation_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Initial load
        self.refresh_patient_list()
    
    def create_menu(self):
        """Create menu bar with database management options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Database menu
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=db_menu)
        
        db_menu.add_command(label="Clear All Data", command=self.clear_all_data_confirm)
        db_menu.add_separator()
        db_menu.add_command(label="Delete Selected Patient", command=self.delete_selected_patient)
        db_menu.add_separator()
        db_menu.add_command(label="Exit", command=self.root.quit)

    def clear_all_data_confirm(self):
        """Confirm and clear all database data"""
        response = messagebox.askyesnocancel(
            "⚠️ Clear All Data",
            "WARNING: This will permanently delete ALL patients and consultations!\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure?",
            icon='warning'
        )
        
        if response:
            # Double confirmation
            confirm = messagebox.askyesno(
                "⚠️ Final Confirmation",
                "Last chance! Really delete EVERYTHING?",
                icon='warning'
            )
            
            if confirm:
                success = self.agent.clear_all_data()
                if success:
                    messagebox.showinfo("Success", "All data has been cleared.")
                    self.refresh_patient_list()
                    self.patient_info_text.config(state=tk.NORMAL)
                    self.patient_info_text.delete(1.0, tk.END)
                    self.patient_info_text.config(state=tk.DISABLED)
                    self.current_patient_id = None
                    self.current_conversation_id = None
                else:
                    messagebox.showerror("Error", "Failed to clear data.")

    def delete_selected_patient(self):
        """Delete the currently selected patient"""
        if not self.current_patient_id:
            messagebox.showwarning("No Selection", "Please select a patient first.")
            return
        
        patient_info = self.agent.get_patient_info(self.current_patient_id)
        
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete patient: {patient_info['name']} ({self.current_patient_id})?\n\n"
            "This will delete all their consultations and history.\n"
            "This action cannot be undone!",
            icon='warning'
        )
        
        if response:
            success = self.agent.clear_patient_data(self.current_patient_id)
            if success:
                messagebox.showinfo("Success", f"Patient {patient_info['name']} has been deleted.")
                self.current_patient_id = None
                self.refresh_patient_list()
                self.patient_info_text.config(state=tk.NORMAL)
                self.patient_info_text.delete(1.0, tk.END)
                self.patient_info_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Failed to delete patient.")

    def refresh_patient_list(self):
        """Refresh the patient listbox"""
        self.patient_listbox.delete(0, tk.END)
        patients = self.agent.get_all_patients()
        
        for patient in patients:
            display_text = f"{patient['name']} ({patient['patient_id']}) - {patient['age']}y, {patient['gender']}"
            self.patient_listbox.insert(tk.END, display_text)
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selection = self.patient_listbox.curselection()
        if not selection:
            return
        
        # Extract patient ID from selection
        selected_text = self.patient_listbox.get(selection[0])
        patient_id = selected_text.split('(')[1].split(')')[0]
        
        self.current_patient_id = patient_id
        self.display_patient_info(patient_id)
        self.start_consultation_btn.config(state=tk.NORMAL)
    
    def display_patient_info(self, patient_id: str):
        """Display patient information and history"""
        patient_info = self.agent.get_patient_info(patient_id)
        patient_history = self.agent.get_patient_history(patient_id)
        
        self.patient_info_text.config(state=tk.NORMAL)
        self.patient_info_text.delete(1.0, tk.END)
        
        if patient_info:
            info_text = f"ID: {patient_info['patient_id']}\n"
            info_text += f"Name: {patient_info['name']}\n"
            info_text += f"Age: {patient_info['age']}\n"
            info_text += f"Gender: {patient_info['gender']}\n"
            info_text += f"Registered: {patient_info['created_at']}\n\n"
            
            info_text += "=== PREVIOUS VISITS ===\n"
            if patient_history:
                for i, visit in enumerate(patient_history, 1):
                    info_text += f"\nVisit {i}:\n"
                    info_text += f"Date: {visit['session_date']}\n"
                    info_text += f"Complaint: {visit['chief_complaint']}\n"
            else:
                info_text += "No previous visits\n"
            
            self.patient_info_text.insert(1.0, info_text)
        
        self.patient_info_text.config(state=tk.DISABLED)
    
    def open_new_patient_dialog(self):
        """Open dialog to register new patient"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New Patient")
        dialog.geometry("400x250")
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="Patient ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        patient_id_entry = ttk.Entry(dialog, width=30)
        patient_id_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Age:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        age_entry = ttk.Entry(dialog, width=30)
        age_entry.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Gender:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(dialog, textvariable=gender_var, width=28)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=3, column=1, padx=10, pady=10)
        
        def register():
            patient_id = patient_id_entry.get().strip()
            name = name_entry.get().strip()
            age = age_entry.get().strip()
            gender = gender_var.get()
            
            if not all([patient_id, name, age, gender]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            try:
                age = int(age)
            except ValueError:
                messagebox.showerror("Error", "Age must be a number!")
                return
            
            success = self.agent.register_patient(patient_id, name, age, gender)
            
            if success:
                messagebox.showinfo("Success", f"Patient {name} registered successfully!")
                self.refresh_patient_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"Patient ID {patient_id} already exists!")
        
        ttk.Button(dialog, text="Register", command=register).grid(row=4, column=0, columnspan=2, pady=20)
    
    def start_consultation(self):
        """Start a new consultation"""
        if not self.current_patient_id:
            messagebox.showerror("Error", "Please select a patient first!")
            return
        
        # Ask for chief complaint
        complaint = simpledialog.askstring("Chief Complaint", 
                                              "Enter the chief complaint:",
                                              parent=self.root)
        
        if not complaint:
            return
        
        # Create new conversation
        self.current_conversation_id = self.agent.create_conversation(
            self.current_patient_id, 
            complaint
        )
        
        # Enable chat interface
        self.send_btn.config(state=tk.NORMAL)
        self.end_consultation_btn.config(state=tk.NORMAL)
        
        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        # Display consultation start
        self.chat_display.insert(tk.END, f"=== CONSULTATION STARTED ===\n", "system")
        self.chat_display.insert(tk.END, f"Patient: {self.current_patient_id}\n", "system")
        self.chat_display.insert(tk.END, f"Chief Complaint: {complaint}\n", "system")
        self.chat_display.insert(tk.END, f"{'='*40}\n\n", "system")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send a message to the AI assistant"""
        if not self.current_conversation_id:
            messagebox.showerror("Error", "No active consultation!")
            return
        
        message = self.message_input.get(1.0, tk.END).strip()
        if not message:
            return
        
        # Display user message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Doctor: ", "user")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Clear input
        self.message_input.delete(1.0, tk.END)
        
        # Disable send button while processing
        self.send_btn.config(state=tk.DISABLED, text="Processing...")
        self.root.update()
        
        try:
            # Get AI response
            response = self.agent.chat(
                self.current_patient_id,
                self.current_conversation_id,
                message
            )
            
            # Display AI response
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "Assistant: ", "assistant")
            self.chat_display.insert(tk.END, f"{response}\n\n")
            self.chat_display.insert(tk.END, f"{'-'*40}\n\n", "system")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get response: {str(e)}")
        
        finally:
            # Re-enable send button
            self.send_btn.config(state=tk.NORMAL, text="Send")
    
    def end_consultation(self):
        """End the current consultation with automated summarization"""
        if not self.current_conversation_id:
            messagebox.showerror("Error", "No active consultation!")
            return
        
        # Show processing message
        self.end_consultation_btn.config(text="Generating Summary...", state=tk.DISABLED)
        self.root.update()
        
        try:
            # Generate automated summary
            summary_data = self.agent.generate_consultation_summary(self.current_conversation_id)
            
            # Fill in the fields automatically
            self.summary_entry.delete(0, tk.END)
            self.summary_entry.insert(0, summary_data['summary'])
            
            self.symptoms_entry.delete(0, tk.END)
            self.symptoms_entry.insert(0, summary_data['symptoms'])
            
            self.diagnoses_entry.delete(0, tk.END)
            self.diagnoses_entry.insert(0, summary_data['diagnoses'])
            
            # Ask for confirmation
            response = messagebox.askyesno(
                "Review Summary",
                "AI has generated the consultation summary. Would you like to review/edit before saving?\n\n"
                "Click 'Yes' to review and edit\n"
                "Click 'No' to save as is"
            )
            
            if response:  # User wants to review
                self.end_consultation_btn.config(text="Save Consultation", state=tk.NORMAL)
                messagebox.showinfo("Review Mode", 
                                "Please review the Summary, Symptoms, and Diagnoses fields below.\n"
                                "Edit if needed, then click 'Save Consultation' when ready.")
                
                # Change button to save mode
                self.end_consultation_btn.config(command=self.save_consultation_after_review)
                return
            
            # User clicked No - save immediately
            self.save_final_consultation(summary_data['summary'], 
                                        summary_data['symptoms'], 
                                        summary_data['diagnoses'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {str(e)}")
            self.end_consultation_btn.config(text="End Consultation", state=tk.NORMAL)

    def save_consultation_after_review(self):
        """Save consultation after user has reviewed/edited the summary"""
        summary = self.summary_entry.get().strip()
        symptoms = self.symptoms_entry.get().strip()
        diagnoses = self.diagnoses_entry.get().strip()
        
        if not all([summary, symptoms, diagnoses]):
            messagebox.showwarning("Warning", "Please ensure all fields are filled!")
            return
        
        self.save_final_consultation(summary, symptoms, diagnoses)

    def save_final_consultation(self, summary: str, symptoms: str, diagnoses: str):
        """Final save of consultation to database"""
        # Save consultation
        self.agent.end_conversation(
            self.current_conversation_id,
            summary,
            symptoms,
            diagnoses
        )
        
        # Display end message in chat
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n" + "="*60 + "\n", "system")
        self.chat_display.insert(tk.END, "=== CONSULTATION ENDED ===\n", "system")
        self.chat_display.insert(tk.END, f"Summary: {summary}\n", "system")
        self.chat_display.insert(tk.END, f"Symptoms: {symptoms}\n", "system")
        self.chat_display.insert(tk.END, f"Diagnoses: {diagnoses}\n", "system")
        self.chat_display.insert(tk.END, "="*60 + "\n", "system")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Reset UI
        self.send_btn.config(state=tk.DISABLED)
        self.end_consultation_btn.config(text="End Consultation", state=tk.DISABLED, 
                                        command=self.end_consultation)
        self.current_conversation_id = None
        
        # Clear summary fields
        self.summary_entry.delete(0, tk.END)
        self.symptoms_entry.delete(0, tk.END)
        self.diagnoses_entry.delete(0, tk.END)
        
        # Refresh patient info to show new visit
        self.display_patient_info(self.current_patient_id)
        
        messagebox.showinfo("Success", "Consultation saved successfully!")