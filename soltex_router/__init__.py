from setuptools import setup, find_packages

setup(
    name="soltex_router",
    version="0.1.0"
    description="Solana zero-gas, MEV-protected intent router SDK for AI Agents",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SOLTEX_ROUTER",
    packages=find_packages(),
    install_requires=[
        "solders>=0.21.0",
        "requests>=2.31.0",
        "base58>=2.1.1"
    ],
    python_requires=">=3.8",
)
