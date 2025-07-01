
import tkinter as tk
from tkinter import ttk # ttk is a themed widget set that provides a more modern look and feel than the standard Tkinter widgets.
from tkinter import messagebox
import serial
import time
import pandas as pd
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

Start_Time = None  # to store the first Arduino time

# -------- Serial Setup --------


# Set up serial connection (update COM port as needed)
ser = serial.Serial('COM28', 9600)  # Replace COM?? with your port
time.sleep(1)  # Wait for connection to establish

# --- Plot Setup ---
#plt.ion()  # Turn on interactive mode

# Buffers to store the last N points (adjust maxlen as needed)
time_vals = deque(maxlen=200)
target_angles = deque(maxlen=200)
current_angles = deque(maxlen=200)
torques = deque(maxlen=200)

# --- Storage for Excel ---
all_data = {
    "Time(s)": [],
    "Target Angle": [],
    "Current Angle": [],
    "Torque": []
}

# -------- GUI Setup -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
root = tk.Tk() # Create the main Tkinter window
root.title("Live Plot + Save GUI") # Set the title of the window

# --- Frame: Controls ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
control_frame = ttk.Frame(root) # Create a frame to hold the controls (label, entry, button)
control_frame.pack(padx=10, pady=5, fill='x') # padx and pady add padding around the frame, fill='x' makes it expand horizontally.

ttk.Label(control_frame, text="Name:").pack(side='left') # Create a label for the name entry field, side='left' places it to the left of the entry field.
name_entry = ttk.Entry(control_frame, width=30) # Create an entry field for the name, width=30 sets the width of the entry field.
name_entry.pack(side='left', padx=5) # padx=5 adds horizontal padding between the label and entry field.
# --- Save button with fuction---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def save_data():# This function will save the data to an Excel file.
    name = name_entry.get().strip() # Get the name from the entry field and remove any leading/trailing spaces.
    if not name:
        messagebox.showwarning("Missing Name", "Please enter a name before saving.")# If the name is empty, show a warning message and return. messagebox is a simple way to show a dialog box with a message.
        return
    df = pd.DataFrame(all_data)#pd.DataFrame converts the all_data dictionary into a DataFrame, which is a 2D labeled data structure with columns of potentially different types.
    filename = f"{name}_tracking_data.xlsx"
    # Correct way to join path remeber to declare os.path first.
    save_path = os.path.join("C:\\Users\\YF80KY\\OneDrive - Aalborg Universitet\\Desktop\\VIEXO_Shoulder Exo\\controller_new_for_exo\\data", filename)#os.path.join is used to create a full file path by joining the directory and filename. This ensures that the file is saved in the specified directory.
 
    df.to_excel(save_path, index=False)#By default, pandas will write the DataFrame’s row index (0, 1, 2, …) as a leftmost column in Excel. Setting index=False tells pandas not to include that index column, so your Excel file will only contain the actual data columns you defined.
    messagebox.showinfo("Saved", f"Data saved as '{filename}'.") # This will show a message box to confirm the save operation.

save_button = ttk.Button(control_frame, text="Save", command=save_data) # This button will call the save_data function when clicked.
save_button.pack(side='left', padx=5) #side='left' places the button to the left of the label and entry, and padx=5 adds horizontal padding. #save_button.pack ensures the button is displayed in the control frame.

# --- Frame: Plot ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4)) # Create a figure and axis for the plot, figsize sets the size of the figure in inches. fig means figure and ax means axis. plt.subplots() is a function that creates a figure and a set of subplots. It returns a tuple containing the figure and axes objects.
canvas = FigureCanvasTkAgg(fig, master=root) # Create a canvas to embed the matplotlib figure in the Tkinter window. FigureCanvasTkAgg is a class that allows you to embed a matplotlib figure in a Tkinter window. master=root means the canvas will be a child of the root window.
canvas.get_tk_widget().pack(padx=10, pady=5) # This packs the canvas into the Tkinter window, padx and pady add padding around the canvas.

# --- Live Loop ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def update_plot():#if you declare it as function, then you have to use global for previously declared values, otherwise it will create a local variable with the same name.
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip() # while data available from the serial.serial port, Converts the raw bytes into a human-readable string, remove any extra white spaces.
            #print(line)
            try: # Attempt to parse the line, if error occurs jump to except. this block should be in-line with line code.
               parts = line.split(",") # This splits the string into parts using comma+space as the separator.
               if len(parts) != 4:
                  raise ValueError("Invalid format")

               time_val = parts[0].split(":")[1].strip().replace("ms", "") # 0th part is the time. removing space after spliting and replace ms with nothing.
               target_angle = parts[1].split(":")[1].strip() # 1st part is the target_angle. removing space after spliting.
               current_angle = parts[2].split(":")[1].strip()# 2nd part is the current angle. removing space after spliting.
               torque = parts[3].split(":")[1].strip()# 3rd part  is the torque_value. removing space after spliting .


               t = float(time_val)/1000  # Convert time string to float values and then divide by 1000 to convert milliseconds to seconds.
               
               global Start_Time  # Use the global variable to track the start time
               if Start_Time is None:  # Initialize Start_Time on the first read since inside function you cannot acess start time as it will creat local variavble insteade of taking the global variable declared first.. you need to use global keyword.
                  Start_Time = t  # Set the start time to the first read time
               t = t - Start_Time  # Calculate the elapsed time since the start
               
               
               
               target = float(target_angle)
               current = float(current_angle)
               torque_1 = float(torque)
            
               # Store in buffer appending values to the deque.
               time_vals.append(t)
               target_angles.append(target)
               current_angles.append(current)
               #torques.append(torque_1)

               all_data["Time(s)"].append(t) # Append the value to the all_data dictionary.
               all_data["Target Angle"].append(target)
               all_data["Current Angle"].append(current)
               all_data["Torque"].append(torque_1)


               # --- Plotting ---
               ax.clear()  # Clear previous plot
               ax.plot(time_vals, target_angles, label='Target Angle', color='red')
               ax.plot(time_vals, current_angles, label='Current Angle', color='green')
               ax.set_xlabel('Time (s)')
               ax.set_ylabel('Angle (°)')
               ax.set_title('Live Angle Tracking')
               ax.legend()
               ax.grid(True)
               #ax.pause(0.01)  # Pause briefly to allow update
               canvas.draw()

               print(f"Time(ms): {time_vals}, Target: {target_angles}, Current: {current_angles}, Torque: {torques}")
            except Exception as e:
               print("⚠️ Parse error:", e)
               print("⚠️ Problem line:", line)

            
        root.after(10, update_plot)  # Call again after 10 ms

# Start the loop
root.after(10, update_plot)

# Run the app
root.mainloop()
 # Convert to DataFrame and save

#----------------------------------
#df = pd.DataFrame(all_data)
#df.to_excel("angle_tracking_data.xlsx", index=False)
#print("✅ Excel file saved as 'angle_tracking_data.xlsx'.")

#ser.close()

#------------------------ Read Excel file
#df = pd.read_excel("C:\\Users\\YF80KY\\OneDrive - Aalborg Universitet\Desktop\\VIEXO_Shoulder Exo\\controller_new_for_exo\\data\\data_1.xlsx")  # Replace with your file name
#df.columns = ["Time_raw(s)", "Time(s)", "Reference", "Current Position", "error"]
#df["Time(s)"] = df["Time(s)"]
#data= {    "Time(s)": df["Time(s)"].tolist(),
   #         "Reference": df["Reference"].tolist(),
   #         "Current Position": df["Current Position"].tolist(),
   #         "error": df["error"].tolist()
           
#}


#dff =pd.DataFrame(data)
# Save to CSV
#dff.to_csv("C:\\Users\\YF80KY\\OneDrive - Aalborg Universitet\\Desktop\\VIEXO_Shoulder Exo\\controller_new_for_exo\\data\\demo_1.csv", index=False)  
# Print the data
#print(df)