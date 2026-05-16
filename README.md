# LIBRARY MANAGEMENT SYSTEM

## Project Overview:
The Library Management System is a web application that allows users to efficiently manage a library's operations. The system will cater to both admins and users, providing functionalities like book registration, user registration, book search, book rental, purchase options, and other essential library management tasks. The system must be mobile responsive and ensure a seamless user experience with live validation for all input forms.

## General Requirements:
*   The system must be mobile-responsive, providing an optimal user experience on various devices.

## User Registration:
*   The registration form must have live form validation for fields like name, email, and password.
*   Passwords must meet minimum security requirements (e.g., minimum length, special characters, numbers).
*   Email addresses must be unique, and the system should display an error if the email is already registered.
*   Upon successful registration, the user must receive a confirmation email to the user with the randomly generated 6-digit number as a password and can later reset the password as needed.

## User Login:
*   Users must have the option to reset their passwords using a secure and user-friendly password reset process and it must have the proper form live validation as mentioned above in registration.
*   Users should have the ability to update their profile information and should be able to reset their passwords securely.

## Admin Features:
*   Upon successful user registration, the admin must receive a notification in the dashboard to approve the user.
*   Admin must have the ability to add books with details such as book stock, book name, author name, publisher ID, and price.
*   Admins should be able to view, edit, and delete existing book records.
*   Admins must be able to view all registered users and their rental history details and their book purchase history.

## User Features
*   Users should be able to search for books by name and author name.
*   The system must display the real-time availability status of books.
*   Users must have the ability to rent books, specifying the rental period and receiving a due date.
*   In case a user loses a rented book, they should be able to report it as lost through the system. The system should calculate the fine amount, which includes the book's original price and any additional charges.
*   Users should have access to a section where they can view their rented book history.
*   The system should automatically alert users and admins when a rental exceeds its due date.
*   If a user fails to return a book on time, the system must calculate and display fines accordingly.

## Book Purchase
*   Users should be able to purchase books from anywhere in the world using secure payment options.
*   The purchase process should involve an "add to cart" feature with the ability to increment and decrement quantities of selected books.
*   Users must receive a confirmation email for their purchase with order details.

---

## 🛠️ Technology Stack
*   **Backend Framework**: Django 5.x (Python)
*   **Database**: MySQL
*   **Frontend**: HTML, CSS, JavaScript, Bootstrap (via Django Templates)
*   **Payment Gateway**: Razorpay API
*   **Image Processing**: Pillow

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone <your-repository-url>
cd Library_Management_System
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure the Database**
*   Open your MySQL client and create a database named `librarydb`:
    ```sql
    CREATE DATABASE librarydb;
    ```
*   Ensure your MySQL credentials match the `DATABASES` configuration in `Library_Management_System/settings.py`.

**5. Apply Migrations & Run Server**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
