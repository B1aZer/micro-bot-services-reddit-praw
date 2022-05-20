source venv/bin/activate
watchmedo3 auto-restart --pattern "*.py;*.js"--recurve --signal SIGTERM python3.9 handler.py >> log.log
