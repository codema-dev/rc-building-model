from setuptools import setup
import versioneer

requirements = ["pandas"]
dev_requires = ["black"]
test_requires = ["pytest", "pytest-cov"]
extras = {
    "dev": test_requires + dev_requires,
}

setup(
    name="rc-building-model",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A Resistance Capacitance (RC) Model for the Simulation of Building Stock Energy Usage",
    license="MIT",
    author="Rowan Molony",
    author_email="rowan.molony@codema.ie",
    url="https://github.com/rdmolony/rc-building-model",
    packages=["rc_building_model"],
    entry_points={"console_scripts": ["rc_building_model=rc_building_model.cli:cli"]},
    install_requires=requirements,
    extras_require=extras,
    keywords="rc-building-model",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
