#!/usr/bin/env python3
"""
Main entry point for Heroku deployment
"""

from web_app_heroku import app

if __name__ == '__main__':
    app.run()