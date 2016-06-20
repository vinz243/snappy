
import os
import urllib
from shutil import copyfile
import hashlib
import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def sha1(str):
    sha1 = hashlib.sha1()
    sha1.update(str)
    return sha1.hexdigest()

def serialize(data, id):
    return

def load(data, id):
    return

def normalize_id(id):
    return id.replace('.', '_').replace(':', '__')


def read_remote_file(url, invalidate_cache=False):
    if url.startswith('local:'):
        return ''

    if not os.path.isdir(os.getcwd() + '/buck-out/'):
        print 'Run script from main dir'
        exit(1)

    cksum = sha1(url)
    dir = os.getcwd() + '/buck-out/cache/{0}/{1}/'.format(cksum[0:2], cksum[2:4])
    mkdir_p(dir)

    cache = dir + cksum

    if os.path.isfile(cache):
        if invalidate_cache:
            os.remove(file)
            return read_remote_file(url)
        else:
            return open(cache, 'r').read()

    rf = urllib.urlopen(url)

    if rf.getcode() == 404:
        lf = open(cache, 'w')
        lf.write('')
        return ''

    content = rf.read()

    lf = open(cache, 'w')
    lf.write(content)
    return content
