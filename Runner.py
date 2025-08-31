import nltk
from nltk.downloader import Downloader

d = Downloader()
installed_packages = [pkg.id for pkg in d.packages() if d.is_installed(pkg.id)]
print(installed_packages)

packages = ['omw-1.4', 'stopwords', 'wordnet', 'words']

for pkg in packages:
    nltk.download(pkg)
