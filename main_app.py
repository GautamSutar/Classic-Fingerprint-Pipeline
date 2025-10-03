from dotenv import load_dotenv
import fingerprint_engine  
import psycopg2 
import sqlite3
import time
import json
import sys
import os

DB_PATH = os.path.join('database', 'user_data.db')
load_dotenv()
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
MATCH_SCORE_THRESHOLD = 50  
SCANNER_PORT = 'COM3'

def scan_fingerprint_from_device():
    try:
        from pyfingerprint.pyfingerprint import PyFingerprint
    except ImportError:
        print("\n--- SCANNER ERROR ---")
        print("The 'pyfingerprint' library is not installed.")
        print("Please run: pip install pyfingerprint")
        return None
    try:
        f = PyFingerprint(SCANNER_PORT, 57600, 0xFFFFFFFF, 0x00000000)
        if (f.verifyPassword() == False):
            print("Could not connect to the fingerprint sensor!")
            return None
    except Exception as e:
        print("\n--- SCANNER ERROR ---")
        print(f"Could not initialize the sensor on port '{SCANNER_PORT}'.")
        print(f"Error: {e}")
        print("Please check your SCANNER_PORT setting and device connection.")
        return None
    print("\nSensor initialized. Waiting for a finger...")
    while (f.readImage() == False):
        time.sleep(0.1)
    print("Finger detected! Processing...")
    os.makedirs('temp', exist_ok=True)
    temp_file = f"temp/scan_template{time.strftime('%Y%m%d_%H%M%S')}.png"
    f.downloadImage(temp_filename)
    print(f"Fingerprint image saved to: {temp_filename}")
    return temp_filename
    
def get_image_from_user():
    while True:
        print("How Would you like to provide the fingerprint ?")
        print("[1] Enter a file path")
        print("[2] Use fingerprint scanner")
        choice = input("Enter your choice (1-2): ")
        if choice == '1':
            path = input("Enter the full path of image: ")
            if not os.path.exists(path):
                print(f"Error: This file path: {path} does not exist")
                continue
            return path
        elif choice == '2':
            scan_image_path = scan_fingerprint_from_device()
            if scan_image_path:
                return scan_image_path
            else:
                print("Scanning failed. Please try again or choose another option.")
                continue
        else:
            print("Invalid choice. Please enter 1 or 2.") 
        
def get_db_connections():
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        return conn
    except psycopg2.OperationalError as e:
        print(f"--- DATABASE CONNECTION ERROR ---")
        print(f"Could not connect to the database: {e}")
        print("Please check your DB_CONNECTION_STRING in the .env file.")
        return None

def setup_database():
    conn = get_db_connections()
    if conn is None:
        print("Error: conn ---> does not have anything")
        return 
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            details TEXT,
            fingerprint_template TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print("Database is set up and ready.")
    

def enroll_user():
    print("\n--- New User Enrollment ---")
    name = input("Enter user's name: ")
    details = input("Enter any other details (e.g., email, ID number): ")
    
    image_path = get_image_from_user()
    if not os.path.exists(image_path):
        print("Error: Image file not found.")
        return
     
    print("Processing fingerprint... Please wait.")
    template = fingerprint_engine.preprocess_and_extract(image_path)

    if not template:
        print("Error: Could not process fingerprint. Please use a clearer image.")
        return

    template_json = json.dumps(template)
    conn = get_db_connections()
    if conn is None:
        return 
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, details, fingerprint_template) VALUES (%s, %s, %s)",
                       (name, details, template_json))
        conn.commit()
        print(f"\nSuccess! User '{name}' has been enrolled in the cloud database.")
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()
    

def verify_user():
    print("\n--- User Verification ---")
    name_to_verify = input("Enter the name of the user want to verify: ")
    conn = get_db_connections()
    if conn is None:
        return
    user_record = None
    try:
        cursor = conn.cursor()
        # --- FIX 3: Remove the extra '?' from the SQL statement ---
        sql = "SELECT id, name, details, fingerprint_template FROM users WHERE name = %s"
        cursor.execute(sql, (name_to_verify,))
        user_record = cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()

    if user_record is None:
        print(f"Error: No user with the name '{name_to_verify}' found in the database.")
        return

    image_path = get_image_from_user()
    if not os.path.exists(image_path):
        print("Error: Image file not found.")
        return
    candidate_template = fingerprint_engine.preprocess_and_extract(image_path)
    if not candidate_template:
        print("Error: Could not process fingerprint.")
        return
    _id, name, details, stored_template_json = user_record 
    stored_template = json.loads(stored_template_json)
    print(f"Comparing provided fingerprint against the stored template for '{name}'...")
    score = fingerprint_engine.compare_templates(candidate_template, stored_template)
    print(f"\nMatch Score: {score:.2f}%")

    if score >= MATCH_SCORE_THRESHOLD:
        print("\n--- Verification Successful! ---")
        print(f"Welcome, {name}!")
        print(f"Retrieved Details: {details}")
    else:
        print("\n--- Verification Failed ---")
        print("The provided fingerprint does not match the stored record.")
        
def main_menu():
    setup_database()
    while True:
        print("\n===== Fingerprint Authentication System =====")
        print("1. Enroll a New User")
        print("2. Verify an Existing User")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        if choice == '1':
            enroll_user()
        elif choice == '2':
            verify_user()
        elif choice == '3':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
if __name__ == '__main__':
    main_menu()
    
