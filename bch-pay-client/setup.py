#!/usr/bin/env python3
"""
Setup script tradicional para bch-pay-client.
Alternativa a pyproject.toml/poetry.
"""

from setuptools import setup, find_packages
import os

# Leer README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Dependencias
install_requires = [
    "requests>=2.31",
]

extras_require = {
    "qr": ["qrcode>=7.4", "pillow>=10.0"],
    "web": ["flask>=3.0", "fastapi>=0.104", "uvicorn>=0.24"],
    "telegram": ["python-telegram-bot>=20.0"],
    "discord": ["discord.py>=2.3"],
    "all": [
        "qrcode>=7.4",
        "pillow>=10.0",
        "flask>=3.0",
        "fastapi>=0.104",
        "uvicorn>=0.24",
        "python-telegram-bot>=20.0",
        "discord.py>=2.3"
    ]
}

setup(
    name="bch-pay-client",
    version="0.1.0",
    author="BCH x IA Team",
    author_email="team@bch-ia.org",
    description="Bitcoin Cash payment client for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/y42bvf6695-gif/bch-pay-client",
    project_urls={
        "Bug Tracker": "https://github.com/y42bvf6695-gif/bch-pay-client/issues",
        "Documentation": "https://github.com/y42bvf6695-gif/bch-pay-client/docs",
        "Source Code": "https://github.com/y42bvf6695-gif/bch-pay-client",
    },
    packages=find_packages(exclude=["examples", "tests", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="bitcoin-cash bch payments ai-agents blockchain llm gpu compute rental marketplace",
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "bchpay-cli=examples.agent_cli:main",
            "bchpay-agent=examples.agent_hybrid:main",
        ],
    },
    include_package_data=True,
    license="MIT",
)