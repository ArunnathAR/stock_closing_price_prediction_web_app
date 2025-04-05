import streamlit as st
import pandas as pd
import hashlib
import secrets
import re
from database import add_user, check_user_exists, verify_user

def hash_password(password):
    """Hash a password for storing."""
    salt = secrets.token_hex(8)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                   salt.encode('utf-8'), 100000)
    pwdhash = pwdhash.hex()
    return salt + pwdhash

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:16]
    stored_hash = stored_password[16:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), 
                                   salt.encode('utf-8'), 100000)
    pwdhash = pwdhash.hex()
    return pwdhash == stored_hash

def initialize_authentication():
    """Initialize the authentication system."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.authenticated

def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None

def login():
    """Display login form and handle login."""
    st.markdown('<h3 class="title-text">Login</h3>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not username or not password:
                st.error("Please fill in all fields.")
                return
            
            # Verify user
            user_id, status, stored_password = verify_user(username)
            
            if status:
                if verify_password(stored_password, password):
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success("Login successful!")
                    # Rerun to refresh the page
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
            else:
                st.error("Username not found. Please sign up.")

def signup():
    """Display signup form and handle signup."""
    st.markdown('<h3 class="title-text">Create an Account</h3>', unsafe_allow_html=True)
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Sign Up")
        
        if submit_button:
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
                return
            
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email address.")
                return
            
            # Check password strength
            if len(password) < 8:
                st.error("Password must be at least 8 characters long.")
                return
            
            # Check if passwords match
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            # Check if username already exists
            if check_user_exists(username):
                st.error("Username already exists. Please choose another one.")
                return
            
            # Hash password and add user to database
            hashed_password = hash_password(password)
            user_id = add_user(username, email, hashed_password)
            
            if user_id:
                st.success("Account created successfully! You can now log in.")
            else:
                st.error("An error occurred while creating your account. Please try again.")
