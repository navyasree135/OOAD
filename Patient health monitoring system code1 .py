import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt
import pandas as pd  # Import pandas for Excel export
import os  # To check current working directory

# Database Connection
conn = sqlite3.connect("patient_monitoring.db")
cursor = conn.cursor()

# Create Tables if Not Exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    condition TEXT NOT NULL,
                    heart_rate INTEGER,
                    temperature REAL,
                    health_problem TEXT,
                    treatment_required TEXT NOT NULL)''')

# Check if medications column exists and add it if it doesn't
try:
    cursor.execute("SELECT medications FROM patients LIMIT 1")
except sqlite3.OperationalError:
    cursor.execute("ALTER TABLE patients ADD COLUMN medications TEXT")
    print("Added medications column to patients table")

# Check if diet_plan column exists and add it if it doesn't
try:
    cursor.execute("SELECT diet_plan FROM patients LIMIT 1")
except sqlite3.OperationalError:
    cursor.execute("ALTER TABLE patients ADD COLUMN diet_plan TEXT")
    print("Added diet_plan column to patients table")

conn.commit()

# Method 1: Add Default Doctor User if No Users Exist
def add_default_doctor():
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:  # If no users exist
        username = "doctor1"
        password = "password123"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, "doctor"))
        conn.commit()
        print("Default doctor user added: Username = doctor1, Password = password123")

# Run the function to ensure a doctor user exists
add_default_doctor()

# Function to export patient data to an Excel file
def export_to_excel():
    try:
        cursor.execute("SELECT * FROM patients")
        data = cursor.fetchall()
        
        if data:
            columns = ["ID", "Name", "Age", "Condition", "Heart Rate", "Temperature", 
                      "Health Problem", "Treatment Required", "Medications", "Diet Plan"]
            df = pd.DataFrame(data, columns=columns)
            
            # Get the current working directory
            current_directory = os.getcwd()
            print("Current Directory:", current_directory)

            # Save to the current directory
            df.to_excel(os.path.join(current_directory, "patients.xlsx"), index=False, engine="openpyxl")
            messagebox.showinfo("Success", "Patient data exported to patients.xlsx")
        else:
            messagebox.showwarning("No Data", "No patient data available to export.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while exporting data: {str(e)}")

# Tkinter App
class PatientApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Patient Health Monitoring System")
        self.root.geometry("400x300")

        tk.Label(root, text="Username").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.login).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get().encode("utf-8")

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user[2].encode("utf-8")):
            role = user[3]
            messagebox.showinfo("Success", f"Login successful! Role: {role}")
            if role == "doctor":
                self.open_doctor_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_doctor_dashboard(self):
        self.doctor_win = tk.Toplevel(self.root)
        self.doctor_win.title("Doctor Dashboard")
        self.doctor_win.geometry("1100x500")  # Increased width for new columns

        tk.Label(self.doctor_win, text="Patient Management", font=("Arial", 14)).pack()

        # Search Frame
        search_frame = tk.Frame(self.doctor_win)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search by Name or ID:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_patients).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Clear Search", command=self.load_patients).pack(side=tk.LEFT, padx=5)

        # Treeview Setup
        columns = ("ID", "Name", "Age", "Condition", "Heart Rate", "Temperature", 
                  "Health Problem", "Treatment Required", "Medications", "Diet Plan")
        self.tree = ttk.Treeview(self.doctor_win, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)  # Adjusted width to fit more columns

        self.tree.pack(expand=True, fill="both")

        # Button Frame
        button_frame = tk.Frame(self.doctor_win)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Patient", command=self.add_patient_window).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit Patient", command=self.edit_patient_window).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_patients).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export to Excel", command=export_to_excel).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Learning Journal", command=self.open_learning_journal).pack(side=tk.LEFT, padx=5)

        self.load_patients()

    def open_learning_journal(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient to view/update learning journal!")
            return
            
        patient_data = self.tree.item(selected_item, "values")
        patient_id = patient_data[0]
        patient_name = patient_data[1]
        
        journal_win = tk.Toplevel(self.root)
        journal_win.title(f"Learning Journal for {patient_name}")
        journal_win.geometry("600x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(journal_win)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Daily tracking tab
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="Daily Tracking")
        
        # Weekly summary tab
        weekly_frame = ttk.Frame(notebook)
        notebook.add(weekly_frame, text="Weekly Summary")
        
        # Monthly report tab
        monthly_frame = ttk.Frame(notebook)
        notebook.add(monthly_frame, text="Monthly Report")
        
        # Patient info at the top
        tk.Label(daily_frame, text=f"Patient: {patient_name}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Show current medications and diet
        tk.Label(daily_frame, text="Current Medications:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Label(daily_frame, text=patient_data[8] if len(patient_data) > 8 and patient_data[8] else "None prescribed").grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Current Diet Plan:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Label(daily_frame, text=patient_data[9] if len(patient_data) > 9 and patient_data[9] else "None prescribed").grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Daily tracking section
        tk.Label(daily_frame, text="Daily Progress Tracker", font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Label(daily_frame, text="Date:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        date_entry = tk.Entry(daily_frame, width=20)
        date_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Medication Adherence:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        med_var = tk.StringVar(value="Yes")
        tk.Radiobutton(daily_frame, text="Yes", variable=med_var, value="Yes").grid(row=5, column=1, sticky="w", padx=10, pady=5)
        tk.Radiobutton(daily_frame, text="No", variable=med_var, value="No").grid(row=5, column=1, sticky="e", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Diet Compliance:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        diet_var = tk.StringVar(value="Yes")
        tk.Radiobutton(daily_frame, text="Yes", variable=diet_var, value="Yes").grid(row=6, column=1, sticky="w", padx=10, pady=5)
        tk.Radiobutton(daily_frame, text="No", variable=diet_var, value="No").grid(row=6, column=1, sticky="e", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Symptoms:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        symptoms_entry = tk.Text(daily_frame, width=40, height=3)
        symptoms_entry.grid(row=7, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Side Effects:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        side_effects_entry = tk.Text(daily_frame, width=40, height=3)
        side_effects_entry.grid(row=8, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Mood (1-10):").grid(row=9, column=0, sticky="w", padx=10, pady=5)
        mood_scale = tk.Scale(daily_frame, from_=1, to=10, orient=tk.HORIZONTAL, length=200)
        mood_scale.grid(row=9, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(daily_frame, text="Notes:").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        notes_entry = tk.Text(daily_frame, width=40, height=5)
        notes_entry.grid(row=10, column=1, sticky="w", padx=10, pady=5)
        
        def save_journal():
            messagebox.showinfo("Success", "Journal entry saved successfully!")
        
        tk.Button(daily_frame, text="Save Entry", command=save_journal, width=20).grid(row=11, column=0, columnspan=2, pady=20)
        
        # Weekly summary tab content
        tk.Label(weekly_frame, text=f"Weekly Summary for {patient_name}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=10)
        
        tk.Label(weekly_frame, text="Week Starting:").pack(anchor="w", padx=10, pady=5)
        tk.Entry(weekly_frame, width=20).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(weekly_frame, text="Progress Summary:").pack(anchor="w", padx=10, pady=5)
        tk.Text(weekly_frame, width=50, height=5).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(weekly_frame, text="Medication Compliance Rate (%):").pack(anchor="w", padx=10, pady=5)
        tk.Scale(weekly_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(weekly_frame, text="Diet Compliance Rate (%):").pack(anchor="w", padx=10, pady=5)
        tk.Scale(weekly_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(weekly_frame, text="Challenges Faced:").pack(anchor="w", padx=10, pady=5)
        tk.Text(weekly_frame, width=50, height=5).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(weekly_frame, text="Adjustments Needed:").pack(anchor="w", padx=10, pady=5)
        tk.Text(weekly_frame, width=50, height=5).pack(anchor="w", padx=10, pady=5)
        
        tk.Button(weekly_frame, text="Save Weekly Summary", width=20).pack(anchor="center", pady=20)

    def search_patients(self):
        """Search patients by name or ID"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showinfo("Info", "Please enter a search term")
            return
            
        # Clear current view
        self.tree.delete(*self.tree.get_children())
        
        # Check if the search term is a number (ID)
        try:
            # If it's an integer, search by ID
            patient_id = int(search_term)
            cursor.execute("""
                SELECT id, name, age, condition, heart_rate, temperature, health_problem, treatment_required, medications, diet_plan 
                FROM patients 
                WHERE id = ?
            """, (patient_id,))
        except ValueError:
            # If not an integer, search by name (partial match)
            cursor.execute("""
                SELECT id, name, age, condition, heart_rate, temperature, health_problem, treatment_required, medications, diet_plan 
                FROM patients 
                WHERE name LIKE ?
            """, (f"%{search_term}%",))
        
        # Display results
        results = cursor.fetchall()
        for row in results:
            self.tree.insert("", "end", values=row)
            
        # Show message if no results found
        if not results:
            messagebox.showinfo("Search Results", "No matching patients found")

    def load_patients(self):
        """Load all patients into the Treeview"""
        self.tree.delete(*self.tree.get_children())
        cursor.execute("SELECT id, name, age, condition, heart_rate, temperature, health_problem, treatment_required, medications, diet_plan FROM patients")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_patient_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Patient")
        add_win.geometry("400x550")  # Increased size for new fields

        tk.Label(add_win, text="Name").pack()
        name_entry = tk.Entry(add_win)
        name_entry.pack()

        tk.Label(add_win, text="Age").pack()
        age_entry = tk.Entry(add_win)
        age_entry.pack()

        tk.Label(add_win, text="Condition").pack()
        condition_entry = tk.Entry(add_win)
        condition_entry.pack()

        tk.Label(add_win, text="Health Problem").pack()
        health_problem_entry = tk.Entry(add_win)
        health_problem_entry.pack()

        tk.Label(add_win, text="Treatment Required").pack()
        treatment_entry = tk.Entry(add_win)
        treatment_entry.pack()
        
        # New fields for medications and diet plan
        tk.Label(add_win, text="Medications").pack()
        medications_entry = tk.Entry(add_win, width=40)
        medications_entry.pack()
        
        tk.Label(add_win, text="Diet Plan").pack()
        diet_plan_entry = tk.Entry(add_win, width=40)
        diet_plan_entry.pack()

        def save_patient():
            name = name_entry.get()
            age = age_entry.get()
            condition = condition_entry.get()
            health_problem = health_problem_entry.get()
            treatment = treatment_entry.get()
            medications = medications_entry.get()
            diet_plan = diet_plan_entry.get()

            if not treatment:
                messagebox.showerror("Error", "Treatment Required cannot be empty!")
                return

            heart_rate = 80
            temperature = 37.0

            cursor.execute("""
                INSERT INTO patients 
                (name, age, condition, heart_rate, temperature, health_problem, treatment_required, medications, diet_plan) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, age, condition, heart_rate, temperature, health_problem, treatment, medications, diet_plan))
            conn.commit()
            export_to_excel()  # Update Excel file after adding a patient
            messagebox.showinfo("Success", "Patient added successfully!")
            add_win.destroy()
            self.load_patients()

        tk.Button(add_win, text="Save", command=save_patient).pack(pady=10)

    def edit_patient_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient to edit!")
            return

        patient_data = self.tree.item(selected_item, "values")
        patient_id = patient_data[0]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Patient")
        edit_win.geometry("400x550")  # Increased size for new fields

        tk.Label(edit_win, text="Name").pack()
        name_entry = tk.Entry(edit_win)
        name_entry.insert(0, patient_data[1])
        name_entry.pack()

        tk.Label(edit_win, text="Age").pack()
        age_entry = tk.Entry(edit_win)
        age_entry.insert(0, patient_data[2])
        age_entry.pack()

        tk.Label(edit_win, text="Condition").pack()
        condition_entry = tk.Entry(edit_win)
        condition_entry.insert(0, patient_data[3])
        condition_entry.pack()

        tk.Label(edit_win, text="Health Problem").pack()
        health_problem_entry = tk.Entry(edit_win)
        health_problem_entry.insert(0, patient_data[6])
        health_problem_entry.pack()

        tk.Label(edit_win, text="Treatment Required").pack()
        treatment_entry = tk.Entry(edit_win)
        treatment_entry.insert(0, patient_data[7])
        treatment_entry.pack()
        
        # New fields for medications and diet plan
        tk.Label(edit_win, text="Medications").pack()
        medications_entry = tk.Entry(edit_win, width=40)
        medications_entry.insert(0, patient_data[8] if len(patient_data) > 8 and patient_data[8] else "")
        medications_entry.pack()
        
        tk.Label(edit_win, text="Diet Plan").pack()
        diet_plan_entry = tk.Entry(edit_win, width=40)
        diet_plan_entry.insert(0, patient_data[9] if len(patient_data) > 9 and patient_data[9] else "")
        diet_plan_entry.pack()

        def update_patient():
            cursor.execute("""
                UPDATE patients 
                SET name=?, age=?, condition=?, health_problem=?, treatment_required=?, medications=?, diet_plan=? 
                WHERE id=?
                """, (name_entry.get(), age_entry.get(), condition_entry.get(), health_problem_entry.get(), 
                      treatment_entry.get(), medications_entry.get(), diet_plan_entry.get(), patient_id))
            conn.commit()
            export_to_excel()  # Update Excel file after updating a patient
            messagebox.showinfo("Success", "Patient details updated!")
            edit_win.destroy()
            self.load_patients()

        tk.Button(edit_win, text="Update", command=update_patient).pack(pady=10)

if __name__ == "_main_":
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()
