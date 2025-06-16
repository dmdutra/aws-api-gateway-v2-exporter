from setuptools import setup, find_packages

setup(
    name='prometheus-api-gateway-v2-exporter',
    version='0.0.1',
    description='Prometheus exporter for AWS API Gateway v2',
    url='https://github.com/sockstat/aws-api-gateway-v2-exporter',
    author='Gabriel M. Dutra',
    author_email="me@sockstat.xyz",
    entry_points={"console_scripts": ["prometheus-api-gateway-v2-exporter=exporter.__main__:main"]},
    install_requires=[
        'boto3',
        'prometheus_client'
    ],
    zip_safe=False,
    packages=find_packages()
)
