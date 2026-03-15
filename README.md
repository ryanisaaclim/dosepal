# DosePal

DosePal is a medication adherence monitoring system designed to help elderly patients—particularly those with dementia or short-term memory challenges—manage their daily medications.

The system combines a reminder-based pill dispenser concept with a web-based monitoring application that allows caregivers or family members to track medication adherence remotely.

🔗 **Live Demo**  
https://dosepal.onrender.com

---

# Project Overview

DosePal was developed as a **Final Year Project for the Diploma in Biomedical Engineering at Nanyang Polytechnic**.

The project explores how assistive reminder devices combined with digital monitoring tools can help improve medication adherence among elderly patients.

The system focuses on improving communication between **patients and caregivers** by providing visibility into whether medications have been taken, missed, or delayed.

The current version of DosePal focuses primarily on the **software platform**, which simulates how a smart medication reminder system could operate alongside a physical pill dispenser.

---

# Smart Pill Dispenser (Hardware)

A physical pill dispenser prototype was built to remind patients when it is time to take their medication.

Features include:

- **LED indicator** that lights up when it is time for medication
- **Buzzer alert** to notify the patient
- Simple and intuitive interaction designed for elderly users

When the patient takes the medication, the action can be simulated or recorded and reflected in the monitoring system.

---

# Target Users

DosePal is designed for:

- **Elderly patients with dementia**
- **Patients with short-term memory impairment**
- **Caregivers managing medication schedules for elderly family members**

The system aims to reduce missed medications and provide caregivers with reassurance that medications are being taken as scheduled.

---

# Application Preview

## Dashboard

The main dashboard displays the user's medication schedule for the day.

Key features include:

- Daily medication progress tracking
- Upcoming and overdue medication reminders
- Clear medication status indicators
- Quick action buttons to mark medications as taken

The dashboard is designed to allow caregivers to quickly determine whether medications have been taken or missed.

---

## Medication Scheduling

The scheduling interface allows users to add medications and configure reminder times.

Users can:

- Add new medications
- Set medication times
- Configure recurring daily medications
- Modify or remove existing medication entries

This allows caregivers to easily maintain and update medication schedules.

---

## Medication History

The history log records medication events and provides a record of adherence behaviour.

Each entry records:

- Medication name
- Scheduled time
- Action performed (taken or missed)
- Timestamp of the event

This allows caregivers to review past medication activity and monitor adherence patterns.

---

# Features

- Medication scheduling system
- Medication status tracking (Upcoming / Overdue / Taken)
- Daily adherence progress tracking
- Medication history logging
- Caregiver monitoring dashboard
- Medication management interface
- Simulated hardware interaction for medication intake

---

# Technology Stack

## Backend

- Python
- Flask

## Frontend

- HTML
- CSS

## Database

- SQLite

## Deployment

- Render

---

# System Architecture

DosePal follows a simple client–server architecture.

User / Caregiver
↓
Web Browser
↓
Flask Application (app.py)
↓
Application Logic
↓
SQLite Database
↓
Response returned to Browser


The browser interface communicates with the Flask backend, which processes application logic and retrieves or stores medication data in the SQLite database.

---

# Project Structure

dosepal/
│
├── app.py
├── requirements.txt
├── dosepal.db
│
├── templates/
│ ├── index.html
│ ├── add.html
│ ├── edit.html
│ ├── history.html
│ ├── device.html
│ └── layout.html
│ ├── login.html
│ └── register.html
│ ├── analytics.html
│
├── static/
│ └── style.css


---

# Future Improvements

Although the current version demonstrates the core idea of a medication management system, several improvements could enhance the system further.

### Real Hardware Integration

Future versions could integrate the web application with the physical pill dispenser so that medication intake is automatically recorded when the patient interacts with the device.

### Real-Time Notifications

Caregivers could receive alerts when medications are missed or delayed through push notifications, SMS, or email.

### User Roles and Authentication

Future versions could support multiple user roles such as patients, caregivers, and administrators.

### Advanced Medication Scheduling

Possible additions include:

- Multiple doses per day
- Dosage instructions
- Recurring medication plans
- Temporary medication changes

### Accessibility Improvements

Since the system targets elderly users, the interface could be enhanced with:

- Larger buttons
- Higher contrast
- Voice prompts
- Simplified navigation

### Security and Data Protection

Future versions should include stronger authentication and improved data protection to handle sensitive healthcare information.

---

# Author

Developed by **Ryan Isaac**  
Diploma in Biomedical Engineering  
Nanyang Polytechnic
