from flask import render_template
from src.web_server.app import app


@app.route('/')
def index():
    """root"""
    return render_template('index.html')

@app.errorhandler(500)
def internal_error(error):
    """internal error"""
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    """not found error handler"""
    app.logger.debug("happened not found error")
    return render_template('errors/404.html'), 404
