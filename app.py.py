import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import datetime
import time
from datetime import timedelta
import requests



# Initialize session state attributes
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'login_success' not in st.session_state:
    st.session_state.login_success = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'caretaker_username' not in st.session_state:
    st.session_state.caretaker_username = ""
if 'device_id' not in st.session_state:
    st.session_state.device_id = ""
if 'selected_section' not in st.session_state:
    st.session_state.selected_section = None  # Store active section


# Load CSV data
caretakers_df = pd.read_csv('caregiver.csv')  # CSV for caretakers
elderly_df = pd.read_csv('elderly.csv') 
# Load daily reminders CSV
daily_reminders_df = pd.read_csv('daily_reminder.csv')
health_df = pd.read_csv("health_monitoring.csv")
safety_df = pd.read_csv("safety_monitoring.csv")

#Function to check elderly login
def elderly_login(device_id, password):
    elderly_record = elderly_df[elderly_df['device_id'] == device_id]
    if not elderly_record.empty:
        if elderly_record.iloc[0]['password'] == password:
            return elderly_record.iloc[0]
    return None

# Function to check caretaker login
def caretaker_login(username, password):
    caretaker_record = caretakers_df[caretakers_df['username'] == username]
    if not caretaker_record.empty:
        if caretaker_record.iloc[0]['password'] == password:
            return caretaker_record.iloc[0]
    return None

def show_elderly_patients(caretaker_username):
    st.markdown(
    """
    <style>
    .stApp {
        background-color: #b2daf7;
    }

    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 30px;
    }

    .device-id-name {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 50px;
        background-color: rgba(255,255,255,0.3);
        padding: 15px 25px;
        margin-bottom: 10px;
        border-radius: 10px;
    }

    .device-id, .device-name {
        font-size: 20px;
        font-weight: bold;
        color: #1E5B8C;
    }

    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    patients = elderly_df[elderly_df['caretaker_username'] == caretaker_username]

    if not patients.empty:
        st.markdown('<div class="mood-header">Elderly Patient Under You</div>', unsafe_allow_html=True)
        for _, patient in patients.iterrows():
            st.markdown(
                f"""
                <div class='device-id-name'>
                    <div class='device-id'>DEVICE ID: {patient['device_id']}</div>
                    <div class='device-name'>NAME: {patient['name']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.write("No elderly patients are assigned to you.")

# Show daily reminders
# Function to fetch reminders for the logged-in elderly based on device ID
# Function to fetch reminders from the CSV file for a specific device_id
def fetch_reminders(device_id):
    # Filter reminders based on the device_id
    return daily_reminders_df[daily_reminders_df['device_id'] == device_id]

# Show daily reminders for the elderly user
def show_daily_reminders(device_id):
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }
    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st.markdown('<div class="mood-header">Daily Reminders</div>', unsafe_allow_html=True)
    
    # Default reminders to always display (done reminders)
    default_reminders = [
        {"reminder_type": "Morning Walk", "scheduled_time": "06:00:00", "acknowledged": 1},
        {"reminder_type": "Breakfast", "scheduled_time": "08:00:00", "acknowledged": 1},
        {"reminder_type": "Juice", "scheduled_time": "11:00:00", "acknowledged": 1},
        {"reminder_type": "Dinner", "scheduled_time": "19:00:00", "acknowledged": 0},
    ]
    
    # Display default reminders first (done reminders)
    for reminder in default_reminders:
        reminder_type = reminder['reminder_type']
        scheduled_time = reminder['scheduled_time']

        # Display as done for default reminders
        reminder_status = "Done" if reminder['acknowledged'] == 1 else "Pending"
        status_symbol = "✅" if reminder['acknowledged'] == 1 else "⏳"
        st.markdown(f"- {reminder_type} at {scheduled_time} - {status_symbol} {reminder_status}")

    # Fetch reminders from the CSV file for the given device_id
    reminders_df = fetch_reminders(device_id)
    
    # Display reminders from the CSV
    if not reminders_df.empty:
        for index, row in reminders_df.iterrows():
            reminder_type = row['reminder_type']
            scheduled_time = pd.to_datetime(row['scheduled_time']).strftime("%I:%M:%S %p")  # Format time as 12-hour time

            if row['acknowledged'] == 0:
                # Reminder not acknowledged, display as pending
                reminder_status = "Pending"
                st.markdown(f"- {reminder_type} at {scheduled_time} - ⏳ {reminder_status}")
            else:
                # Reminder acknowledged, display as done with a checkmark
                reminder_status = "Done"
                st.markdown(f"- {reminder_type} at {scheduled_time} - ✅ {reminder_status}")
    else:
        st.write("No reminders found in the CSV for this device.")

def show_daily_reminders_caregiver(caretaker_username):
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }
    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        }


    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
    # Get all elderly patients under this caregiver
    patients = elderly_df[elderly_df['caretaker_username'] == caretaker_username]
    
    if not patients.empty:
        # Create a selectbox for the caregiver to choose a patient (device_id)
        device_ids = patients['device_id'].tolist()
        selected_device_id = st.selectbox("Select a Patient", device_ids, format_func=lambda x: f"Patient {x}")
        
        # Display default reminders first (done reminders)
        default_reminders = [
            {"reminder_type": "Morning Walk", "scheduled_time": "06:00:00", "acknowledged": 1},
            {"reminder_type": "Breakfast", "scheduled_time": "08:00:00", "acknowledged": 1},
            {"reminder_type": "Juice", "scheduled_time": "11:00:00", "acknowledged": 1},
            {"reminder_type": "Dinner", "scheduled_time": "19:00:00", "acknowledged": 0},
        ]
        
        # Display default reminders first
        st.markdown(f'<div class="mood-header">Daily Reminders for Patient with Device ID: {selected_device_id}</div>', unsafe_allow_html=True)

        for reminder in default_reminders:
            reminder_type = reminder['reminder_type']
            scheduled_time = reminder['scheduled_time']

            # Display as done for default reminders
            reminder_status = "Done" if reminder['acknowledged'] == 1 else "Pending"
            status_symbol = "✅" if reminder['acknowledged'] == 1 else "⏳"
            st.markdown(f"- {reminder_type} at {scheduled_time} - {status_symbol} {reminder_status}")
        
        # Fetch the reminders for the selected patient
        reminders = daily_reminders_df[daily_reminders_df['device_id'] == selected_device_id]
        
        if not reminders.empty:
            
            
            # Display reminders from the CSV in the same format as the elderly dashboard
            for index, row in reminders.iterrows():
                reminder_type = row['reminder_type']
                scheduled_time = pd.to_datetime(row['scheduled_time']).strftime("%I:%M:%S %p")  # Format time as 12-hour time
                
                # Check if the reminder is acknowledged or pending
                if row['acknowledged'] == 0:
                    # Reminder not acknowledged, display as pending
                    reminder_status = "Pending"
                    status_symbol = "⏳"
                else:
                    # Reminder acknowledged, display as done with a checkmark
                    reminder_status = "Done"
                    status_symbol = "✅"
                
                # Display reminder with time, status, and the appropriate symbol
                st.markdown(f"- {reminder_type} at {scheduled_time} - {status_symbol} {reminder_status}")
        else:
            st.write(f"No daily reminders available for this patient.")
    else:
        st.write("No elderly patients are assigned to you.")

def show_patient_data(caretaker_username):
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }
    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        }


    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
     /* Styling for health and safety metrics in horizontal layout */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        align-items: center;
    }
     /* Make metric names blue and bold with larger font */
    .metric-name {
        color: #1E5B8C !important;
        font-size: 24px; /* Increased font size */
        font-weight: bold; /* Bold text */
        width: 40%;
        text-align: left;
    }
    .metric-value {
        font-size: 40px;
        font-weight: bold;
        width: 40%;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)
    # Get the list of patients for the caretaker
    patients = elderly_df[elderly_df['caretaker_username'] == caretaker_username]
    
    if not patients.empty:
        # Create a dropdown to select a patient
        device_ids = patients['device_id'].tolist()
        selected_device_id = st.selectbox("Select a Patient", device_ids, format_func=lambda x: f"Patient {x}")
        
        # Display the health and safety data for the selected patient
        st.markdown(f'<div class="mood-header">Health and Safety Data for Patient {selected_device_id}</div>', unsafe_allow_html=True)
        
        # Display Health Monitoring Data
        health_data = health_df[health_df['device_id'] == selected_device_id]
        if not health_data.empty:
            st.subheader("Health Monitoring Data")
            for index, row in health_data.iterrows():
                timestamp = pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                heart_rate = row['heart_rate']
                heart_rate_flag = row['heart_rate_flag']
                blood_pressure = row['blood_pressure']
                bp_flag = row['bp_flag']
                glucose = row['glucose_levels']
                glucose_flag = row['glucose_flag']
                oxygen = row['oxygen_saturation']
                oxygen_flag = row['oxygen_flag']
                caregiver_notified = row['caregiver_notified']

                # Set the alert color based on the flags
                heart_rate_class = "alert-red" if heart_rate_flag == 1 else "alert-green"
                bp_class = "alert-red" if bp_flag == 1 else "alert-green"
                glucose_class = "alert-red" if glucose_flag == 1 else "alert-green"
                oxygen_class = "alert-red" if oxygen_flag == 1 else "alert-green"
                
                # Display timestamp
                st.markdown(f"<p class='blue-timestamp'>{timestamp}</p>", unsafe_allow_html=True)
                
                # Display each metric with its respective color and value
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Heart Rate</div><div class='metric-value {heart_rate_class}'>{heart_rate} BPM</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Blood Pressure</div><div class='metric-value {bp_class}'>{blood_pressure}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Glucose Levels</div><div class='metric-value {glucose_class}'>{glucose} mg/dL</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Oxygen Saturation</div><div class='metric-value {oxygen_class}'>{oxygen}%</div></div>", unsafe_allow_html=True)

                # Display caregiver notification if applicable
                if caregiver_notified == 1:
                    st.markdown(f"<div class='caregiver-notified'><span class='green-tick'>✔</span> Caregiver Notified</div>", unsafe_allow_html=True)
                
                st.markdown("---")  # Add a separator for each data entry

        else:
            st.write(f"No health data available for Patient with Device ID: {selected_device_id}")
        
        # Display Safety Monitoring Data
        safety_data = safety_df[safety_df['device_id'] == selected_device_id]
        if not safety_data.empty:
            st.subheader("Safety Monitoring Data")
            for index, row in safety_data.iterrows():
                timestamp = pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                activity = row['movement_activity']
                fall_detected = row['fall_detected']
                impact_force = row['impact_force']
                inactivity_duration = row['inactivity_duration']
                current_location = row['location']
                caregiver_notified = row['caregiver_notified']
                
                # Set fall detected status
                fall_status = "Fall Detected" if fall_detected == 1 else "No Fall Detected"
                fall_class = "alert-red" if fall_detected == 1 else "alert-green"
                
                # Set caregiver notification
                caregiver_status = "✔ Caregiver Notified" if caregiver_notified == 1 else "❌ Caregiver Notified"
                caregiver_class = "green-tick" if caregiver_notified == 1 else "red-tick"
                
                # Display safety metrics with appropriate styling
                st.markdown(f"<p class='blue-timestamp'>{timestamp}</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Activity</div><div class='metric-value'>{activity}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Fall Detection</div><div class='metric-value {fall_class}'>{fall_status}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Impact Force</div><div class='metric-value'>{impact_force} </div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Duration of Inactivity</div><div class='metric-value'>{inactivity_duration} mins</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-name'>Current Location</div><div class='metric-value'>{current_location}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='caregiver-notified'><span class='{caregiver_class}'>{caregiver_status}</span></div>", unsafe_allow_html=True)

                st.markdown("---")  # Add a separator for each data entry
        
        else:
            st.write(f"No safety data available for Patient with Device ID: {selected_device_id}")
    else:
        st.write("No patients are assigned to you.")
def show_health_data(device_id):
    # Add custom CSS for styling
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
        
    }
    /* Style the header */
        .mood-header {
            background-color: #72bcf2;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
        }
    /* Make metric names blue */
    .metric-name {
        color: #1E5B8C !important;
    }
    .blue-header {
        color: #1E5B8C !important;
    }

    .blue-subheader {
        color: #1E5B8C !important;
    }

    .blue-timestamp {
        color: #1E5B8C !important;
    }

    /* Styling for health metrics in horizontal layout */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
    }

    .metric-name {
        font-size: 20px;
        font-weight: bold;
        width: 40%;
        text-align: left;
    }

    .metric-value {
        font-size: 40px;
        font-weight: bold;
        width: 40%;
        text-align: right;
    }

    /* Alert colors */
    .alert-red {
        color: red;
    }

    .alert-green {
        color: green;
    }

    /* Caregiver notification styling */
    .caregiver-notified {
        color: green;
        font-size: 24px;
        font-weight: bold;
    }

    .green-tick {
        color: green;
        font-size: 30px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    
    # Display welcome message
    st.markdown(f"<h1 class='mood-header'>Welcome, {device_id}!</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='blue-subheader'>Your Health Monitoring Dashboard</h2>", unsafe_allow_html=True)
    
    # Fetch health data based on the device_id
    health_data = health_df[health_df['device_id'] == device_id]
    
    if not health_data.empty:
        # Loop through health data and display each entry
        for index, row in health_data.iterrows():
            timestamp = pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            heart_rate = row['heart_rate']
            heart_rate_flag = row['heart_rate_flag']
            blood_pressure = row['blood_pressure']
            bp_flag = row['bp_flag']
            glucose = row['glucose_levels']
            glucose_flag = row['glucose_flag']
            oxygen = row['oxygen_saturation']
            oxygen_flag = row['oxygen_flag']
            caregiver_notified = row['caregiver_notified']

            # Set the alert color based on the flags
            heart_rate_class = "alert-red" if heart_rate_flag == 1 else "alert-green"
            bp_class = "alert-red" if bp_flag == 1 else "alert-green"
            glucose_class = "alert-red" if glucose_flag == 1 else "alert-green"
            oxygen_class = "alert-red" if oxygen_flag == 1 else "alert-green"
            
            # Display timestamp
            st.markdown(f"<p class='blue-timestamp'>{timestamp}</p>", unsafe_allow_html=True)
            
            # Display each metric with its respective color and value
            st.markdown(f"<div class='metric-container'><div class='metric-name'>Heart Rate</div><div class='metric-value {heart_rate_class}'>{heart_rate} BPM</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-container'><div class='metric-name'>Blood Pressure</div><div class='metric-value {bp_class}'>{blood_pressure}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-container'><div class='metric-name'>Glucose Levels</div><div class='metric-value {glucose_class}'>{glucose} mg/dL</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-container'><div class='metric-name'>Oxygen Saturation</div><div class='metric-value {oxygen_class}'>{oxygen}%</div></div>", unsafe_allow_html=True)

            # Display caregiver notification if applicable
            if caregiver_notified == 1:
                st.markdown(f"<div class='caregiver-notified'><span class='green-tick'>✔</span> Caregiver Notified</div>", unsafe_allow_html=True)
            
            st.markdown("---")  # Add a separator for each data entry
        
    else:
        st.write("No health data found for this device.")
# Daily diary/journaling
def show_deardiary_entry():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }
    
    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown('<div class="mood-header">Dear Diary</div>', unsafe_allow_html=True)
    
    # Create text area for writing the diary entry
    diary_entry = st.text_area("Write your thoughts for today:", "")

    # Initialize the diary entries list in session state if not present
    if 'diary_entries' not in st.session_state:
        st.session_state.diary_entries = []

    # Button to save the diary entry
    if st.button("Save Entry"):
        if diary_entry:
            # Append the new entry to the list
            st.session_state.diary_entries.append(diary_entry)
            st.success("Your entry has been saved.")
        else:
            st.warning("Please write something before saving.")

    # Display the previous diary entries
    if st.session_state.diary_entries:
        st.subheader("Previous Diary Entries")
        for idx, entry in enumerate(st.session_state.diary_entries, 1):
            st.markdown(f"**Entry {idx}:**")
            st.markdown(f"_{entry}_")
            st.markdown("---")
    else:
        st.write("No previous entries found.")
def show_chatbot():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }

    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    # Display header
    st.markdown('<div class="mood-header">Chat with MedMind</div>', unsafe_allow_html=True)

    # Initialize messages in session state if not already present
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])

    # Text input from the user
    user_input = st.chat_input("Ask MedMind a question:", key='Chat_input')

    if user_input:
        # Add user message to chat and session state
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Send the user input to the Ollama API
        try:
            # Display an assistant message placeholder while loading
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.write("Thinking...")

            # API request to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": user_input,
                    "stream": False
                }
            )

            # Process the response
            if response.status_code == 200:
                result = response.json()
                assistant_response = result["response"]
                
                # Replace the placeholder with the actual response
                message_placeholder.write(assistant_response)
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                message_placeholder.write(f"Error: Status code {response.status_code}")
        
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
        
        # Force a rerun to update the chat display
        st.rerun()
# Show chat platform (Elderly <-> Caretaker)

if 'messages' not in st.session_state:
    st.session_state.messages = []




def show_mood_tracker():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }

    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
    }

    /* Style the mood buttons */
    .mood-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }

    .mood-button {
        border: none;
        padding: 20px;
        border-radius: 10px;
        font-size: 48px;
        text-align: center;
        width: 200px;
        cursor: pointer;
        position: relative; /* To position the tooltip */
    }

    .mood-selected {
        background-color: #A084E8 !important;
        color: white !important;
    }

    /* Style the mood analysis */
    .mood-analysis {
        background-color: #b8e8fc;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }

    .suggestion-box {
        background-color: #7ed7fc;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
    }

    /* Custom tooltip for the mood buttons */
    .stButton button[title]:hover::after {
        content: attr(title);
        position: absolute;
        background-color: #1E5B8C;
        color: white;
        border-radius: 5px;
        padding: 5px 10px;
        font-size: 14px;
        /* Position the tooltip to the right of the button */
        right: 100%;
        top: 50%;
        transform: translateY(-50%);
        white-space: nowrap;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="mood-header">Mood Tracker</div>', unsafe_allow_html=True)
    st.subheader("How are you feeling today?")

    # Display today's date
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    st.markdown(f"### {today}")

    # Mood options with emojis
    mood_options = {
        "Happy": "😊",
        "Neutral": "😐",
        "Sad": "😞",
        "Anxious": "😟",
        "Angry": "😠",
        "Excited": "🤩"
    }

    # Initialize selected mood in session state if not already
    if 'selected_mood' not in st.session_state:
        st.session_state.selected_mood = None

    # Create columns for horizontal layout
    cols = st.columns(3)

    # Create buttons for each mood in the columns and apply styling
    for idx, (mood, emoji) in enumerate(mood_options.items()):
        btn_class = "mood-button"
        if st.session_state.selected_mood == mood:
            btn_class += " mood-selected"

        if cols[idx % 3].button(f"{emoji}\n{mood}", key=mood, help=f"Click to select {mood}"):
            st.session_state.selected_mood = mood

    # Mood Analysis Section
    if st.session_state.selected_mood:
        mood_message = {
            "Happy": "You're feeling good and positive!",
            "Neutral": "You're feeling okay, neither good nor bad.",
            "Sad": "You're feeling down or upset.",
            "Anxious": "You're feeling worried or nervous.",
            "Angry": "You're feeling frustrated or irritated.",
            "Excited": "You're feeling pumped and enthusiastic!"
        }

        mood_suggestions = {
            "Sad": "Try listening to calming music or talking to a loved one.",
            "Anxious": "Take a deep breath and try mindfulness exercises.",
            "Angry": "Try some deep breathing or a physical activity to release tension.",
            "Happy": "Great! Keep up the positive energy by engaging in something fun.",
            "Neutral": "Consider engaging in activities to boost your mood.",
            "Excited": "Channel that excitement into a creative or physical activity!"
        }

        # Display mood analysis and suggestions
        st.markdown('<div class="mood-analysis"><b>Mood Analysis</b><br>' + mood_message[st.session_state.selected_mood] + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="suggestion-box"><b>Suggestion</b><br>' + mood_suggestions[st.session_state.selected_mood] + '</div>', unsafe_allow_html=True)

# Show engagement activity
def show_engagement_activity():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }
    /* Style the header */
    .mood-header {
        background-color: #72bcf2;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
    st.markdown('<div class="mood-header">Engagement Activities</div>', unsafe_allow_html=True)
    game = st.selectbox("Select a game to play:", ["Sudoku", "Chess", "Solitaire"], key="game_selectbox")
    
    st.write(f"You have selected: {game}")

    if game == "Sudoku":
        sudoku_embed_code = """
        <div style="display: flex; justify-content: center; align-items: center; height: 5%; padding: 20px;">
            <iframe src="http://www.free-sudoku.com/sudoku-webmaster.php?mescandi1=1&fondspage=FFFFFF&lesliens=4A4C87&coubo1=1C1D3D&couli1=C0C0C2&coucp1=FFFFFF&counp1=000000&counn1=3F428A&couce1=FFFFFF&coune1=FF0000&coucr1=FFFFFF&hauteur111=750" width="500" height="550" frameborder="0"></iframe>
        </div>
        """
        components.html(sudoku_embed_code, width=600, height=830)
    elif game == "Chess":
        chess_embed_code = """
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; padding: 20px;">
            <iframe src="https://play.chessbase.com" style="width:1200px; height:675px; border:none;"></iframe>
        </div>
        """
        components.html(chess_embed_code, height=700)
    elif game == "Solitaire":
        solitaire_embed_code = """<div id="solitaire_embed" style="width:100%;">
  <style>
    @media (max-width: 800px) {
      #solitaire_embed > div {
        padding-bottom: 90% !important; /* Change aspect ratio on mobile */
      }
    }
    @media (max-width: 568px) {
      #solitaire_embed > div {
        padding-bottom: 100% !important; /* Change aspect ratio on mobile */
      }
    }
    @media (max-width: 414px) {
      #solitaire_embed > div {
        padding-bottom: 120% !important; /* Change aspect ratio on mobile */
      }
    }
  </style>
  <div style="position:relative;padding-bottom:75%;border-radius:6px;overflow:hidden;">
    <iframe style="width:100%;height:100%;position:absolute;left:0px;top:0px;border:0px;" frameBorder="0" width="100%" height="100%" allowFullScreen="false" src="https://online-solitaire.com/mslfddxo06" title="Play Klondike (Turn 3) and many more Solitaire games at online-solitaire.com"></iframe>
    <div style="position:absolute;width:100%;height:100%;top:0px;left:0px;pointer-events:none;box-shadow:inset 0px 0px 0px 1px rgba(0,0,0,0.25);border-radius:6px;"></div>
  </div>
  <p style="font-size:16px;line-height:40px;width:100%;text-align:center;margin:0px;">
     </p>
</div>
        """
        components.html(solitaire_embed_code, height=1000)

def meditation_timer():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    /* Style the header */
        .mood-header {
            background-color: #72bcf2;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)
    st.markdown("""
    <style>
        .picker-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            padding: 10px;
            background-color: black;
            color: white;
            border-radius: 10px;
            font-size: 24px;
        }
        .picker {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            min-width: 80px;
        }
        .timer-display {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Time Picker UI ---
    st.markdown('<div class="mood-header">Meditation Timer</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        hours = st.selectbox("Hours", list(range(24)), index=0, key="hour", format_func=lambda x: f"{x} hours")

    with col2:
        minutes = st.selectbox("Minutes", list(range(60)), index=1, key="minute", format_func=lambda x: f"{x} min")

    with col3:
        seconds = st.selectbox("Seconds", list(range(60)), index=0, key="second", format_func=lambda x: f"{x} sec")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Countdown Logic ---
    total_seconds = (hours * 3600) + (minutes * 60) + seconds

    if st.button("Start Timer"):
        if total_seconds > 0:
            end_time = time.time() + total_seconds
            
        
            placeholder = st.empty()  # Placeholder for dynamic timer updates

            while time.time() < end_time:
                remaining = int(end_time - time.time())
                h, m, s = remaining // 3600, (remaining % 3600) // 60, remaining % 60
                placeholder.markdown(f'<div class="timer-display">{h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
        
        # Timer complete
            st.success("🎉 Meditation Session Complete! 🧘‍♂️")
            st.balloons()
        else:
            st.error("Please select a valid duration!")


# Function to show login page
def login_page():
    st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #b2daf7;
    }

    /* Change all text to dark blue */
    * {
        color: #1E5B8C !important;
    }
    </style>
    """,
    unsafe_allow_html=True

    )


    st.title("Welcome to Care Sphere!")
    st.header("Please Login")
    
    user_type = st.radio("Are you an Elderly or Caretaker?", ["Elderly", "Caretaker"])
    
    if user_type == "Elderly":
        device_id = st.text_input("Enter your Device ID")
        password = st.text_input("Enter your Password", type="password")
        if st.button("Login"):
            login_result = elderly_login(device_id, password)
            if login_result is not None:  # Ensure the result is not None
                st.session_state.device_id = device_id
                st.session_state.user_name = login_result['name']
                st.session_state.user_type = "elderly"
                st.session_state.logged_in = True
                st.session_state.login_success = True
                st.session_state.selected_section = "Home"
                st.rerun()  # Re-run the app to update the session state
            else:
                st.error("Invalid credentials. Please try again.")
    
    elif user_type == "Caretaker":
        username = st.text_input("Enter your Username")
        password = st.text_input("Enter your Password", type="password")
        if st.button("Login"):
            login_result = caretaker_login(username, password)
            if login_result is not None:  # Ensure the result is not None
                st.session_state.user_type = "caretaker"
                st.session_state.caretaker_username = username
                st.session_state.logged_in = True
                st.session_state.login_success = True
                st.session_state.selected_section = "Elderly Patients"
                st.rerun()  # Re-run the app to update the session state
            else:
                st.error("Invalid credentials. Please try again.")

# Main function for the app
if __name__ == '__main__':
    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title("NAVIGATION")
        
        if st.session_state.user_type == "elderly":
            if st.sidebar.button("Home"):
                st.session_state.selected_section = "Home"
            if st.sidebar.button("Daily Reminders"):
                st.session_state.selected_section = "Daily Reminders"
            if st.sidebar.button("Mood Tracker"):
                st.session_state.selected_section = "Mood Tracker"
            if st.sidebar.button("Engagement Activity"):
                st.session_state.selected_section = "Engagement Activity"
            if st.sidebar.button("Dear Diary"):
                st.session_state.selected_section = "Dear Diary"
            if st.sidebar.button("MedMind"):
                st.session_state.selected_section = "MedMind"
            if st.sidebar.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.selected_section = None
                st.rerun()  # Re-run to reset the session

        elif st.session_state.user_type == "caretaker":
            if st.sidebar.button("Elderly Patients"):
                st.session_state.selected_section = "Elderly Patients"
            if st.sidebar.button("Patient Daily Reminders"):
                st.session_state.selected_section = "Patient Daily Reminders"
            if st.sidebar.button("Health Data"):
                st.session_state.selected_section = "Health Data"
            if st.sidebar.button("MedMind"):
                st.session_state.selected_section = "MedMind"
            if st.sidebar.button("Meditation Timer"):
                st.session_state.selected_section = "Meditation Timer"
            if st.sidebar.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.selected_section = None
                st.rerun()  # Re-run to reset the session

        # Display the selected section
        if st.session_state.selected_section == "Home":
            show_health_data(st.session_state.device_id)
        elif st.session_state.selected_section == "Daily Reminders":
            show_daily_reminders(st.session_state.device_id)
        elif st.session_state.selected_section == "Mood Tracker":
            show_mood_tracker()
        elif st.session_state.selected_section == "Engagement Activity":
            show_engagement_activity()
        elif st.session_state.selected_section == "Dear Diary":
            show_deardiary_entry()
        elif st.session_state.selected_section == "MedMind":
            show_chatbot()
        elif st.session_state.selected_section == "Elderly Patients":
            show_elderly_patients(st.session_state.caretaker_username)
        elif st.session_state.selected_section == "Patient Daily Reminders":
            show_daily_reminders_caregiver(st.session_state.caretaker_username)
        elif st.session_state.selected_section == "Health Data":
            show_patient_data(st.session_state.caretaker_username)
        elif st.session_state.selected_section == "Meditation Timer":
            meditation_timer()
