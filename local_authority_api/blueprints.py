# Import every blueprint file
from local_authority_api.views import general
from local_authority_api.views.v1_0 import local_authority as local_authority_v1_0
from local_authority_api.views.v1_0 import organisations as organisations_v1_0


def register_blueprints(app):
    """Adds all blueprint objects into the app."""

    app.register_blueprint(general.general)
    app.register_blueprint(local_authority_v1_0.local_authority, url_prefix='/v1.0/local-authorities')
    app.register_blueprint(organisations_v1_0.organisations, url_prefix='/v1.0/organisations')

    # All done!
    app.logger.info("Blueprints registered")
