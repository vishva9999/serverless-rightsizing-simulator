"""
AWS Lambda Handler — Phase 7 ASGI Entry Point.

Wraps the FastAPI application in a Mangum adapter to process Amazon API Gateway
proxy events seamlessly in an AWS Serverless Lambda execution environment.
"""

from mangum import Mangum
from app.main import app

# Initialize Mangum ASGI adapter for FastAPI
handler = Mangum(app, lifespan="off")
