from flask import Flask, jsonify, request, flash, redirect, session
from passlib.hash import pbkdf2_sha256
from backend.src.database.models.models import Register
import uuid

class User:

    def start_session(self, user):
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self, form):

        print(request.form)

        # Create user object
        user = {
            "name": request.form.get('username'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }

        # Check for existing email address
        if Register.objects(email = request.form.get('email')):
            flash('Email already in use!', 'danger')
            return redirect(request.url)
        else:
            flash(f'Account created for {form.username.data}!', 'success')
            Register(
                username = request.form.get('username'),
                email = request.form.get('email'),
                password = request.form.get('password')).save()
            return self.start_session(user)
        return jsonify(user), 200 

    def signout(self):
        session.clear()
        return redirect('/')