import urllib
from shutil import copyfile
from lxml import etree
from lxml import objectify
from io import BytesIO

#
# This is a very quick-n-dirty bucklet for maven packages (jar and aar)
#


import os.path
import errno
import os
import pprint
import dpath.util
import hashlib

def mavensha1(group, name, version, ar, index=0):
    if index == len(repos):
        return None
    try:
        link = repos[index] + '{0}/{1}/{2}/{1}-{2}.{3}.sha1'.format(group.replace('.', '/'), name, version, ar)
        f = urllib.urlopen(link)
        cksum = f.read()
        int(cksum, 16) # will throw an error if cksum is not a hexadecimal string
        cached_repos[cksum] = repos[index]
        return cksum
    except ValueError:
        return mavensha1(group, name, version, ar, index + 1)

# helper for mkdir -p
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise



cached_repos = {}
repos = ['http://repo1.maven.org/maven2/']

def remote_file(**kwargs):
    print 'remote_file ' + kwargs.get('name')

def read_remote_file(url, invalidate_cache=False):
    dir = os.getcwd() + '/buck-out/gen/maven/'

    if not os.path.isdir(os.getcwd() + '/buck-out/'):
        print 'Run script from main dir'
        exit(1)

    mkdir_p(dir)

    sha1 = hashlib.sha1()
    sha1.update(url)
    cksum = sha1.hexdigest()
    cache = dir + cksum

    if os.path.isfile(cache):
        if invalidate_cache:
            os.remove(file)
            return read_remote_file(url)
        else:
            return open(cache, 'r').read()

    print 'warning: not caching '+url +' with cache path '+cache
    rf = urllib.urlopen(url)

    if rf.getcode() == 404:
        lf = open(cache, 'w')
        lf.write('')
        return ''

    content = rf.read()

    lf = open(cache, 'w')
    lf.write(content)
    return content

def mavensha1(group, name, version, ar, index=0):
    if index == len(repos):
        return None
    try:
        link = repos[index] + '{0}/{1}/{2}/{1}-{2}.{3}.sha1'.format(group.replace('.', '/'), name, version, ar)

        cksum = read_remote_file(link)
        int(cksum, 16) # will throw an error if cksum is not a hexadecimal string
        cached_repos[cksum] = repos[index] # we know it exists in this repo
        return cksum
    except ValueError:
        return mavensha1(group, name, version, ar, index + 1)

def dmaven(pkg):
    group, name, version = pkg.split(':', 3)
    for ar in ['aar', 'jar']:
        cksum = mavensha1(group, name, version, ar)
        if cksum != None:
            repo = cached_repos[cksum]
            remote_file(
                name = name + '-maven',
                sha1 = cksum,
                url = make_url(repo, group, name, version, ar),
                out = name + '.' + ar,
            )
            if ar == 'aar':
                android_prebuilt_aar(
                    name = name,
                    aar = ':'+name+'-maven',
                    visibility = ['PUBLIC']
                )
            else:
                prebuilt_jar(
                    name = name,
                    binary_jar = ':' + name + '-maven',
                    visibility = ['PUBLIC']
                )

            return
    print('Not found ' + pkg)

def make_url(repo, group, name, version, ar):
    return repo + '{0}/{1}/{2}/{1}-{2}.{3}'.format(group.replace('.', '/'), name, version, ar)

maven_packages = {}
# pkg = {
#     group =
#     name =
#     version =
#     level = secondary or primary
#     dependencies = [
#         pkg
#     ]
# }
def parse_deps(repo, pkg, level='primary'):

    group, name, version = pkg.split(':', 3)
    if name in maven_packages:
        # if maven_packages[name].level == 'primary':
        return

    pomUrl = make_url(repo, group, name, version, 'pom')

    pom = read_remote_file(pomUrl)
    if pom == '':
        maven_packages[name] = {
            'type': 'local_package',
            'group': group,
            'name': name,
            'version': version,
            'level': level,
        }
        return
    project = objectify.fromstring(pom)

    deps = []

    try:
        for dep in project.dependencies.dependency:
            if dep.scope == 'compile':
                depPkg = dep.groupId + ':' + dep.artifactId + ':' + str(dep.version)
                parse_deps(repo, depPkg, 'secondary')

                deps.append(dep.artifactId)


    except AttributeError:
        pass

    maven_packages[name] = {
        'type': 'remote_maven',
        'group': group,
        'name': name,
        'version': version,
        'repo': repo,
        'dependencies': deps,
        'level': level
    }

def declare_deps():
    for key, value in maven_packages.iteritems():
        if value.type == 'remote_maven':
            maven(pkg)
        elif value.type == 'local_maven':
            local_maven(pkg)

cached_tree = None
def build_dependency_tree(tree={}, package='', path='', only_primary=False):
    global cached_tree
    if package != '':
        value = maven_packages[package]
        if value['level'] != 'primary' and only_primary: return
        new_path = path + '/' + package
        dpath.util.new(tree, new_path, {})
        if 'dependencies' in value:
            for dep in value['dependencies']:
                build_dependency_tree(tree, dep, new_path)
        # elif value.level == 'secondary':

        # else:
            # print 'Unexpected level {0} for {1}'.format(value.level, value.name)

        return

    for key, value in maven_packages.iteritems():
        build_dependency_tree(tree, key, '', True)

    cached_tree = tree

cached_list_deps = []
def build_dependency_list(list_deps, tree, cache=True, prefix=''):
    global cached_list_deps
    if not tree:
        return
    if cache:
        cached_list_deps = list_deps
    for key, value in tree.iteritems():
        pprint.pprint(key)
        if key not in list_deps:
            list_deps.append(prefix+key)
        build_dependency_list(list_deps, value, cache, prefix)

def register_dependencies(list_deps):
    for name in list_deps:
        pkg = maven_packages[name]
        dmaven('{0}:{1}:{2}'.format(pkg['group'], pkg['name'], pkg['version']))

def maven(pkg):
    group, name, version = pkg.split(':', 3)
    for ar in ['aar', 'jar']:
        cksum = mavensha1(group, name, version, ar)
        if cksum != None:
            repo = cached_repos[cksum]
            parse_deps(repo, pkg)
            return

def build_deps(deps):
    global cached_tree
    new_deps = []
    for dep in deps:
        name = dep.split(':', 1)[-1]
        if dep.startswith('//libs:'):
            new_deps.append(dep)
        elif dep.startswith('//mvn:'):
            build_dependency_list(new_deps, cached_tree.get(name), False, '//libs:')
        else: new_deps.append(dep)
    return list(set(new_deps))

# print read_remote_file('http://central.maven.org/maven2/com/facebook/fresco/fbcore/maven-metadata.xml')
maven('com.facebook.fresco:fresco:0.11.0')
# maven('org.springframework:spring-core:4.0.0.RELEASE')


tree = {}
list_deps = []
build_dependency_tree(tree)

build_dependency_list(list_deps, tree)
register_dependencies(list_deps)

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(cached_tree)
pp.pprint(build_deps([
    '//res:res',
    '//libs:support-v4',
    '//mvn:fresco'
]))
