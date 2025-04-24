import tkinter as tk
from tkinter import filedialog, messagebox, Frame, Scrollbar, Text, ttk
import pandas as pd

# Updated recommendations for specific medical conditions
recommendations = {
    "Cancer": {
        "Medications": ["Cyclophosphamide", "Methotrexate"],
        "Treatment": ["Chemotherapy", "Radiation therapy", "Immunotherapy", "Surgery if needed"],
        "Diet": ["High-protein diet", "Nutrient-dense foods", "Avoid processed foods"]
    },
    "Obesity": {
        "Medications": ["Orlistat", "Phentermine (if prescribed)"],
        "Treatment": ["Weight management programs", "Physical activity", "Lifestyle changes"],
        "Diet": ["Low-calorie, high-fiber diet", "Avoid sugary and processed foods"]
    },
    "Diabetes": {
        "Medications": ["Metformin", "Insulin if needed"],
        "Treatment": ["Blood sugar monitoring", "Exercise", "Regular check-ups"],
        "Diet": ["Low-carb, high-protein diet", "Avoid sugary foods and drinks"]
    },
    "Asthma": {
        "Medications": ["Albuterol", "Salbutamol", "Corticosteroids"],
        "Treatment": ["Breathing exercises", "Avoid allergens", "Use air purifiers"],
        "Diet": ["Anti-inflammatory foods", "Avoid dairy and processed foods"]
    },
    "Hypertension": {
        "Medications": ["Amlodipine", "Losartan", "Beta-blockers"],
        "Treatment": ["Stress management", "Regular exercise", "Adequate sleep"],
        "Diet": ["Low-sodium diet", "Potassium-rich foods like bananas and spinach"]
    },
    "Arthritis": {
        "Medications": ["Ibuprofen", "Naproxen", "Methotrexate"],
        "Treatment": ["Physical therapy", "Joint exercises", "Heat/cold therapy"],
        "Diet": ["Anti-inflammatory foods", "Omega-3 rich foods", "Avoid processed sugar"]
    }
}

# Load patient data from CSV file
def load_patient_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            global patient_df
            patient_df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "Patient data loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

# Display patient data by name or ID
def display_patient_data():
    search_value = search_entry.get().strip()
    search_type = search_type_var.get()

    if patient_df is not None and search_value:
        try:
            if search_type == "Patient Name":
                patient = patient_df[patient_df['Name'].astype(str).str.lower() == search_value.lower()]
            elif search_type == "Patient ID":
                patient = patient_df[patient_df['Patient_ID'].astype(str) == search_value]
            else:
                messagebox.showwarning("Invalid Search", "Please select a valid search type.")
                return

            if not patient.empty:
                condition = patient.iloc[0].get('Medical Condition', 'N/A')
                meds = recommendations.get(condition, {}).get('Medications', ['No medication available'])
                treatment = recommendations.get(condition, {}).get('Treatment', ['No treatment available'])
                diet = recommendations.get(condition, {}).get('Diet', ['No diet recommendation available'])

                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Patient Name: {patient.iloc[0].get('Name', 'N/A')}\n")
                result_text.insert(tk.END, f"Patient ID: {patient.iloc[0].get('Patient_ID', 'N/A')}\n")
                result_text.insert(tk.END, f"Medical Condition: {condition}\n\n")
                result_text.insert(tk.END, f"Medications: {', '.join(meds)}\n")
                result_text.insert(tk.END, f"Treatment: {', '.join(treatment)}\n")
                result_text.insert(tk.END, f"Diet: {', '.join(diet)}\n")
                result_text.config(state=tk.DISABLED)

                # Add to search history
                search_history.insert(0, search_value)
                update_search_history()

            else:
                messagebox.showwarning("Not Found", "Patient not found!")
        except KeyError as e:
            messagebox.showerror("Error", f"Column not found: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch patient data: {e}")
#update search history display
def update_search_history():
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    for entry in search_history[:5]:  # Show the last 5 searches
        history_text.insert(tk.END, f"{entry}\n")
    history_text.config(state=tk.DISABLED)

# Create GUI window
root = tk.Tk()
root.title("Patient Health Monitoring System")
root.geometry("800x700")
root.configure(bg='#e0f7fa')

header_label = tk.Label(root, text="Patient Health Monitoring System", font=("Arial", 18, "bold"), bg='#00796b', fg='white')
header_label.pack(pady=10, fill=tk.X)

patient_df = None
search_history = []

# Button to load patient data from CSV
tk.Button(root, text="Load Patient Data (CSV)", command=load_patient_data, bg='#00796b', fg='white', font=("Arial", 12)).pack(pady=10)

# Search type selection
search_frame = Frame(root, bg='#e0f7fa')
search_frame.pack(pady=5)

search_type_var = tk.StringVar(value="Patient Name")
ttk.Combobox(search_frame, textvariable=search_type_var, values=["Patient Name", "Patient ID"], font=("Arial", 12)).pack(pady=10)

# Search entry
search_entry = tk.Entry(root, font=("Arial", 12), width=30)
search_entry.pack(pady=5)

# Button to fetch patient data
tk.Button(root, text="Fetch Patient Data", command=display_patient_data, bg='#004d40', fg='white', font=("Arial", 12)).pack(pady=10)

# Text box for patient data
text_frame = Frame(root, bg='#e0f7fa')
text_frame.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_text = Text(text_frame, font=("Arial", 12), wrap=tk.WORD, yscrollcommand=scrollbar.set, height=10, bg='white', fg='black')
result_text.pack(fill=tk.BOTH, expand=True)
result_text.config(state=tk.DISABLED)
scrollbar.config(command=result_text.yview)

# Search history display
tk.Label(root, text="Recent Searches:", font=("Arial", 12, "bold"), bg='#e0f7fa').pack(pady=5)
history_frame = Frame(root, bg='#e0f7fa')
history_frame.pack(pady=5, fill=tk.BOTH, expand=True)

history_text = Text(history_frame, font=("Arial", 12), wrap=tk.WORD, height=5, bg='white', fg='black')
history_text.pack(fill=tk.BOTH, expand=True)
history_text.config(state=tk.DISABLED)

root.mainloop()


