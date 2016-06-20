from mvn_utils import read_remote_file
from mvn_utils import sha1
from mvn_utils import normalize_id
from lxml import objectify
class MavenPackage(object):
    """docstring for MavenPackage"""
    packages = []

    def find_matching_package(self, group, name=''):
        if name != '':
            pkg = group + ':' + name
        else:
            pkg = group
        for package in MavenPackage.packages:
            if package.data.get('id') == pkg:
                return package
        return None


    def __init__(self, **kwargs):
        self.data = {}

        if not kwargs.get('name') and not kwargs.get('version'):
            group, name, version = kwargs.get('pkg').split(':', 3)

        self.data['name'] = kwargs.get('name') or name
        self.data['version'] = kwargs.get('version') or version
        self.data['group'] = kwargs.get('group') or group
        self.data['dependencies] = []
        self.data['repository'] = None
        self.data['type'] = kwargs.get('type', 'primary')
        self.data['id'] = self.data['group'] + ':' + self.data['name']
        self.data['normalized_id'] =  normalize_id(self.data['id'])
        self.data['package'] = self.data['group'] + ':' + self.data['name'] + ':' + self.data['version']
        # walk tree and look for package with same name
        package = self.find_matching_package(self.data.get('id'))
        if package:
            if package.version != version:
                print 'Duplicate package {0} with different version {1} and {2},'.format(name, version, package.version)
                print '\tdropping {0}#{1}'.format(name, package.version)
                return
            return

        if kwargs.get('repository'):
            self.data['repository'] = kwargs.get('repository')
        else:
            self.find_repository()

        self.build_dependencies()

        MavenPackage.packages.append(self)

    def find_repository(self):
        for ar in ['aar', 'jar']:
            cksum, repo = mavensha1(self.data['group'], self.data['name'], self.data['version'], ar)
            if cksum != None:
                self.data['repository'] = repo
                self.data['checksum'] = cksum
                self.data['file_type'] = ar

                return

    def build_dependencies(self):
        if self.data['repository'] == 'local:':
            return

        pom_url = self.get_url('pom')

        pom = read_remote_file(pom_url)

        # If not found, then local dep
        if pom == '':
            self.data['repository'] = 'local:'
            return

        project = objectify.fromstring(pom)

        try:
            for dep in project.dependencies.dependency:
                if dep.scope == 'compile':
                    self.data.get('dependencies').append(dep.groupId + ':' + dep.artifactId)
                    depPkg = dep.groupId + ':' + dep.artifactId + ':' + str(dep.version)
                    pkg = MavenPackage(pkg=depPkg, type='secondary', repository=self.repository)
        except AttributeError:
            pass

    def display_tree(self, indent=''):

        print indent + self.data['id']
        for dep in self.data['dependencies']:
            self.find_matching_package(dep).display_tree(indent + '  ')

    def get_flat_dependencies(self):
        dep_list = []
        self.get_flat_dependencies2(dep_list)
        return list(set(dep_list))

    def get_flat_dependencies2(self, dep_list):
        dep_list.append(self.data['normalized_id'])
        for dep in self.data['dependencies']:
            self.find_matching_package(dep).get_flat_dependencies2(dep_list)
        return



    def get_url(self, ar):
        return ((self.data['repository'] or 'local:')
                    + '{0}/{1}/{2}/{1}-{2}.{3}'.format(
                        self.data['group'].replace('.', '/'),
                        self.data['name'],
                        self.data['version'], ar))
