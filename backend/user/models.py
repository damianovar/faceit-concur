from flask import Flask, jsonify, request, flash, redirect, session
from passlib.hash import pbkdf2_sha256
from backend.models.models import Register
import uuid

class User:
    def start_session(self, user):
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self, form):

        # Check for existing email address
        if Register.objects(email = request.form.get('email')).first():
            flash('Email already in use!', 'danger')
            return redirect(request.url)
        else:
            flash(f'Account created for {form.username.data}!', 'success')
            user = Register(
                username = request.form.get('username'),
                email = request.form.get('email'),
                password = pbkdf2_sha256.encrypt(request.form.get('password')))
            user.save()
            self.start_session(user.to_json())
            return redirect('/')
        
        return jsonify({"error": "Signup failed"}), 400 

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        user = Register.objects(email=request.form.get('email')).first()
        print(user)
        if user and pbkdf2_sha256.verify(request.form.get('password'), user.password):
            flash('Login successful!', 'success')
            self.start_session(user.to_json())
            return redirect('/')
        else:
            flash('Invalid Username or Password!', 'danger')
            return redirect(request.url)

        return jsonify({"error": "Invalid login credentials "}), 401