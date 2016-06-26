from mvn_utils import read_remote_file
from mvn_utils import sha1
from mvn_utils import normalize_id
from lxml import objectify
import re
import pprint
import traceback

class MavenPackageManager(object):
    def __init__(self, **kwargs):
        self.packages = []

    def register_package(self, pkg):
        old = self.find_matching_package(identifier = pkg.identifier.universal_id)
        if old:
            if old.level < pkg.level:
                old.level = pkg.level
        else:
            self.packages.append(pkg)

    def find_matching_package(self, **kwargs):
        hlp = None
        for pkg in self.packages:
            if self.compare(pkg, kwargs):
                if not hlp or pkg.level > hlp.level:
                    hlp = pkg
        return hlp

    def compare(self, package, kwargs):
        for key, value in kwargs.iteritems():
            obj = getattr(package, key)
            if type(obj) is PackageID:
                return obj.equals(value)
            if obj != value:
                return False
        return True


package_manager = MavenPackageManager()

class PackageID(object):
    def __init__(self, **kwargs):
        self.group = kwargs.get('group')
        self.name = kwargs.get('name')
        self.version = kwargs.get('version')

        # Simple id group:name:version
        self.id = '{0}:{1}:{2}'.format(self.group, self.name, self.version)
        # Hash based id for pkg
        self.hid = sha1(self.id)
        # Shoter version of hash
        self.shid = self.hid[0:5]

        # ID valid across version, group:name
        self.universal_id = '{0}:{1}'.format(self.group, self.name)
        # Hash based id from universal_id
        self.universal_hid = sha1(self.universal_id)
        # Shorter hash id
        self.universal_shid = self.universal_hid[0:5]

        self.normalized_id = self.universal_id.replace('.', '_').replace(':', '__')
    def get_data_holder(self):
        return  {
            'identifier': self.id,
            'universal_id': self.universal_shid
        }

    def equals(self, other):

        pattern = re.compile('([a-z]+_)+_(([a-z]|-)+)')




        if isinstance(other, basestring):
            if self.universal_id == other:
                return True
            if pattern.match(other) and self.normalized_id == other:
                return True
        if (isinstance(other, self.__class__)
            and self.universal_shid == other.universal_shid):
            return True
        return False


def package_id(**kwargs):
    if kwargs.get('package'):
        group, name, version = kwargs['package'].split(':', 3)
        return PackageID(
            group =  group,
            name = name,
            version = version
        )
    else:
        return PackageID(
            group =  kwargs.get('group'),
            name = kwargs.get('name'),
            version = kwargs.get('version')
        )

class MavenPackage(object):
    """docstring for MavenPackage"""
    packages = []

    def __init__(self, **kwargs):
        self.dependencies = []
        self.identifier = package_id(**kwargs)
        self.group = self.identifier.group
        self.name = self.identifier.name
        self.version = self.identifier.version
        self.repository = kwargs['repository'] or 'http://repo1.maven.org/maven2/'
        self.level = kwargs.get('level', 0)
        self.type = kwargs.get('type', 'primary')
        self.build_dependencies()
        package_manager.register_package(self)
    def get_url(self, ar):
        return ((self.repository or 'local:')
                    + '{0}/{1}/{2}/{1}-{2}.{3}'.format(
                        self.group.replace('.', '/'),
                        self.name,
                        self.version, ar))
    def get_data_holder(self):
        return {}
    def build_dependencies(self):
        if self.repository == 'local:':
            return

        pom_url = self.get_url('pom')

        pom = read_remote_file(pom_url)

        # If not found, then local dep
        if pom == '':
            self.repository = 'local:'
            return

        project = objectify.fromstring(pom)

        try:
            for dep in project.dependencies.dependency:
                if dep.scope == 'compile':
                    self.dependencies.append(dep.groupId + ':' + dep.artifactId)
                    depPkg = dep.groupId + ':' + dep.artifactId + ':' + str(dep.version)
                    pkg = MavenPackage(package=depPkg,
                                        level=self.level + 1,
                                        repository=self.repository,
                                        type='secondary')

        except AttributeError:
            pass

    def display_tree(self, indent='', suffix=''):

        print indent + self.identifier.id +' ('+self.identifier.universal_shid + ') @ '+str(self.level) + suffix
        for dep in self.dependencies:
            package_manager.find_matching_package(identifier = dep).display_tree(indent + '  ', suffix)

    def get_flat_dependencies(self, mode=0):
        dep_list = []
        self.get_flat_dependencies2(dep_list, mode)
        return list(set(dep_list))

    def get_flat_dependencies2(self, dep_list, mode=0):
        if mode == 0:
            dep_list.append(self.identifier.normalized_id)
        else:
            dep_list.append(self.identifier.id)
        for dep in self.dependencies:
            package_manager.find_matching_package(identifier = dep).get_flat_dependencies2(dep_list, mode)
        return


    def get_url(self, ar):
        return ((self.repository or 'local:')
                    + '{0}/{1}/{2}/{1}-{2}.{3}'.format(
                        self.group.replace('.', '/'),
                        self.name,
                        self.version, ar))
