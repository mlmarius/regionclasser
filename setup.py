from distutils.core import setup

setup(name='regionclasser',
            version='1.0',
            description="Classify a point into different region classes with respect to Romania.",
            author="Liviu Manea",
            url="https://github.com/mlmarius/regionclasser",
            license="MIT",
            packages=['regionclasser'],
            install_requires=['fiona'],
            zip_safe=False
            )
