
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import time
import pandas as pd
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

start_time = None  # to store the first Arduino time

# -------- Serial Setup --------
ser = serial.Serial('COM28', 9600)  # Replace with your port
time.sleep(2)

# -------- Data Buffers --------
time_vals = deque(maxlen=200)
target_angles = deque(maxlen=200)
current_angles = deque(maxlen=200)

all_data = {
    "Time(s)": [],
    "Target Angle": [],
    "Current Angle": [],
    "Torque": []
}

# -------- GUI Setup --------
root = tk.Tk()
root.title("Live Plot + Save GUI")

# --- Frame: Controls ---
control_frame = ttk.Frame(root)
control_frame.pack(padx=10, pady=5, fill='x')

ttk.Label(control_frame, text="Participant/Trial Name:").pack(side='left')
name_entry = ttk.Entry(control_frame, width=30)
name_entry.pack(side='left', padx=5)

def save_data():
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Missing Name", "Please enter a name before saving.")
        return
    df = pd.DataFrame(all_data)
    filename = f"{name}_tracking_data.xlsx"
    save_path = os.path.join("C:\\Users\\YF80KY\\OneDrive - Aalborg Universitet\\Desktop\\VIEXO_Shoulder Exo\\controller_new_for_exo\\data", filename)
    df.to_excel(save_path, index=False)
    messagebox.showinfo("Saved", f"Data saved as '{filename}'.")

save_button = ttk.Button(control_frame, text="Save", command=save_data)
save_button.pack(side='left', padx=5)

# --- Frame: Plot ---
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(padx=10, pady=5)

# -------- Update Loop --------
def update_plot():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        try:
            parts = line.split(", ")
            if len(parts) != 4:
                raise ValueError("Invalid format")

            time_val = parts[0].split(":")[1].strip().replace("ms", "")
            target_angle = parts[1].split(":")[1].strip()
            current_angle = parts[2].split(":")[1].strip()
            torque = parts[3].split(":")[1].strip()

            t = float(time_val) / 1000
            global start_time
            if start_time is None:
              start_time = t  # Set the initial time once

            t = t - start_time  # Normalize all times to start from 0

            target = float(target_angle)
            current = float(current_angle)
            tq = float(torque)

            # Add to rolling plot
            time_vals.append(t)
            target_angles.append(target)
            current_angles.append(current)

            # Add to full data
            all_data["Time(s)"].append(t)
            all_data["Target Angle"].append(target)
            all_data["Current Angle"].append(current)
            all_data["Torque"].append(tq)

            # --- Update Plot ---
            ax.clear()
            ax.plot(time_vals, target_angles, label="Target Angle", color='red')
            ax.plot(time_vals, current_angles, label="Current Angle", color='blue')
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Angle (°)")
            ax.set_title("Live Angle Tracking")
            ax.legend()
            ax.grid(True)
            canvas.draw()

        except Exception as e:
            print("Parse error:", e)
            print("Line was:", line)

    root.after(10, update_plot)  # Call again after 10 ms

# Start the loop
root.after(10, update_plot)

# Run the app
root.mainloop()

