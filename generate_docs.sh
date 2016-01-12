# Process for setting up sphinx docs taken from here:
# http://raxcloud.blogspot.com/2013/02/documenting-python-code-using-sphinx.html
# git-new-workdir details from here:
# https://thejspr.com/blog/work-on-multiple-branches-with-git-workdir/
#
# sphinx-apidoc generates necessary sphinx files for generating docs, where 'docs'
# is the dir to place files, and 'api/' is the code source
# `sphinx-apidoc -A "clay austin" -F -o docs api/`
# `cd docs`
# edit config.py to set path to include $PWD/espa-api. this is already done for
# version of config.py to be committed. 
# `make html`
# clone git somewhere
# `git clone git@github.com:git/git.git`
# `alias git-new-workdir='<diryouclonedgitto>/git/contrib/workdir/git-new-workdir`
# from top level project dir:
# `mkdir gh-pages`
# `git-new-workdir . gh-pages/html`
# `cd gh-pages/html`
# `git checkout --orphan gh-pages`
# `git rm -rf .`
# `cd ../../docs
# set BUILDDIR in Makefile to '../gh-pages/html'
# `make html`
# html docs will appear in gh-pages/html
 

#git-new-workdir https://thejspr.com/blog/work-on-multiple-branches-with-git-workdir/



