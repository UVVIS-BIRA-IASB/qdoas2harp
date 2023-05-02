from setuptools import setup
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("qdoas2harp").version
except DistributionNotFound:
    pass

if __name__ == "__main__":
    setup()
