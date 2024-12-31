from setuptools import setup, find_packages

setup(
    name="plant_water_reminder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0.0",
        # Add other dependencies if needed
    ],
    description="A simple plant watering reminder app",
    author="Your Name",
    author_email="you@example.com",
)
