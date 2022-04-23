from flask import Flask, render_template, request
import os
secretkey = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = secretkey