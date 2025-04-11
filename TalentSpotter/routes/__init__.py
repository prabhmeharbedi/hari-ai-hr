"""
Routes package for the AI Recruitment System
"""

def init_app(app):
    """Initialize all route blueprints with the app"""
    
    # Import and register all blueprints
    from .main import init_app as init_main
    from .jobs import init_app as init_jobs
    from .candidates import init_app as init_candidates
    from .matches import init_app as init_matches
    from .interviews import init_app as init_interviews
    from .shortlists import init_app as init_shortlists
    
    # Initialize each blueprint
    init_main(app)
    init_jobs(app)
    init_candidates(app)
    init_matches(app)
    init_interviews(app)
    init_shortlists(app)