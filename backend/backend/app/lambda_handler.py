"""Expose the FastAPI app through the AWS Lambda event interface."""

from mangum import Mangum

from app.main import app

handler = Mangum(app)
