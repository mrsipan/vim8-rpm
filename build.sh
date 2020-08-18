#!/bin/bash

set -o verbose
set -o errexit
set -o xtrace

rm *.tar* || true
rm *.rpm || true

curl -OL "https://github.com/vim/vim/archive/v8.2.1477.tar.gz"

gzip -d v8.2.1477.tar.gz
rm v8.2.1477.tar.gz || true

tar -u -f v8.2.1477.tar vim8.spec
gzip -c v8.2.1477.tar > v8.2.1477.tar.gz

rpmbuild -ts --nodeps --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" v8.2.1477.tar.gz

case "$(rpm -q centos-release)" in
  centos-release-7*)
    yum-builddep -y *.src.rpm
    ;;
  centos-release-8*)
    dnf-builddep -y *.src.rpm
    ;;
esac

rpmbuild --rebuild --define "_rpmdir `pwd`/rpms" *.rpm
