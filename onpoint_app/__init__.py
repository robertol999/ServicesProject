from flask import Flask, render_template, request, session, redirect
from onpoint_app.models.costumer import Costumer
from onpoint_app.models.provider import Provider
from onpoint_app.models.job import Job
app = Flask(__name__)

app.secret_key = "secret"