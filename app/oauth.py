# app/oauth.py

# Load environment variables and initialize Auth0 OAuth client with OpenID Connect discovery

import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load .env variables (client ID, secret, domain, etc.)
load_dotenv()

# Create the global OAuth object (we’ll initialize it with app in __init__.py)
oauth = OAuth()

# Register the Auth0 OAuth provider using OpenID Connect discovery
oauth.register(
    name='auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),           # Auth0 application client ID
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),   # Auth0 application client secret

    # Use OpenID Connect metadata to automatically pull jwks_uri, authorization_endpoint, etc.
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',

    # Required scopes to access identity claims like sub, name, email, etc.
    client_kwargs={
        'scope': 'openid profile email'
    }
)
