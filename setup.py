"""Packaging for the on-device LLM mobile toolchain.

Installs the entry points so you can call the tools from anywhere::

    pip install -e .
    chat --model llama-3.2-1b
    download_model qwen2.5
    memory_est --device
"""

from setuptools import find_packages, setup

setup(
    name="on-device-llm-mobile",
    version="0.2.0",
    description="Run quantized LLMs directly on Android phones — catalog, RAM estimator, benchmark, offline chat.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="axe git",
    author_email="axe01010@users.noreply.github.com",
    url="https://github.com/axe01010/on-device-llm-mobile",
    license="MIT",
    packages=find_packages(include=["models", "models.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "odllm-chat=chat:main_cli",
            "odllm-download=download_model:main",
            "odllm-memory=memory_estimator:main",
            "odllm-bench=benchmark:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)