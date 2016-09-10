
from maven_package import MavenPackage
packages = []

def maven_package(**kwargs):

    packages.append(MavenPackage(
        package = kwargs.get('package'),
        repository = kwargs.get('repository'),
        type = kwargs.get('level', 'primary')
    ))
    print kwargs.get('name')

def get_packages():
    return packages
