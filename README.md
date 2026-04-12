BloodCare+

Blood Donation and Request Management System

Project Overview

BloodCare+ is a web-based application developed using Flask to manage blood donation activities in an efficient and organized way. The system provides a centralized platform that connects donors, requesters, volunteers, and administrators, making coordination easier and improving response time during emergency situations.

Objective

The main objective of the system is to:

--> Reduce delays in emergency blood requests
--> Efficiently match compatible donors
--> Support volunteer-based coordination
--> Maintain records of donations and requests
--> Ensure secure, role-based access to the system

User Roles

Administrator

--> Approves or rejects blood requests
--? Manages donors and volunteers
-->Assigns volunteers to requests
--> Monitors the request lifecycle

Donor

--> Registers and updates availability
--> Receives notifications for blood requests
--> Views donation history

Requester

--> Submits new blood requests
--> Tracks request status
--> Views matched donors

Volunteer

--> Accepts assigned tasks
--> Coordinates between donors and requesters
--> Updates task status

Request Lifecycle

Pending → Approved → Assigned → Completed

This workflow ensures proper tracking and transparency of each blood request.

Core Functionalities

--> Role-based authentication using Flask-Login
--> Blood group compatibility matching
--> Location-based donor prioritization
--> Volunteer coordination system
--> Email notifications using Flask-Mail
--> Real-time request status tracking
--> Donation history management
--> CSRF protection for security
--> Modular architecture using Flask Blueprints

Technology Stack

Layer	            Technology

Backend	         -  Flask (Python)
Database	     -  SQLite, SQLAlchemy
Frontend	     -  HTML, CSS, Bootstrap
Authentication	 -  Flask-Login
Email Service	 -  Flask-Mail
Security	     -  CSRF(Cross-Site Request Forgery) Protection

Project Structure

BloodCare/
│
├── app/
│   ├── admin/
│   ├── auth/
│   ├── donor/
│   ├── requester/
│   ├── volunteer/
│   ├── models.py
│   ├── extensions.py
│   ├── utils.py
│
├── static/
├── templates/
├── config.py
├── run.py
├── requirements.txt

Installation and Setup

Clone the repository
--> git clone <repository-url>

Install dependencies
--> pip install -r requirements.txt

Run the application
--> flask run

Open in browser
--> http://127.0.0.1:5000

Security Features

--> Password hashing using Werkzeug
--> Role-based access control
--> CSRF protection
--> Secure configuration management
--> Error handling (403, 404, 500)

Academic Highlights

--> Modular design using Flask Blueprints
--> MVC-based architecture
--> Structured donor matching logic
--> Real-time workflow handling
--> Volunteer task coordination system