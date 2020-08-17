%define debug_package %{nil}
%define patchlevel 0678
%define baseversion 8.2
%define vimdir vim82
%define vimdirsrc vim-%{baseversion}.%{patchlevel}

%define with_selinux 0
%define with_netbeans 0
%define with_vimspell 1
%define with_hunspell 1
%define with_ruby 0
%define with_lua 0
%define python8 python3.8

Name:          vim8
Version:       %{baseversion}.%{patchlevel}
Release:       1%{?dist}
Summary:       The VIM editor
Group:         Applications/Editors
License:       Vim
URL:           http://www.vim.org/
Source0:       https://github.com/vim/vim/archive/v%{baseversion}.%{patchlevel}.tar.gz

Patch3004:     vim-7.0-rclocation.patch
Buildroot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: ncurses-devel
%if %{?rhel}%{!?rhel:0} == 7
BuildRequires: rh-python38-python-devel
%endif

%if %{?rhel}%{!?rhel:0} == 8
BuildRequires: python38-devel
%endif
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: vim-common

%description
VIM (VIsual editor iMproved) is an updated and improved version of the
vi editor.  Vi was the first real screen-based editor for UNIX, and is
still very popular.  VIM improves on vi by adding new features:
multiple windows, multi-level undo, block highlighting and more.

%prep
# change vim directory in github's tgz
if ! tar -tf %{SOURCE0} %{vimdir}/README.txt; then
    cd ../SOURCES
    tar -zxf %{SOURCE0} > /dev/null
    mv %{vimdirsrc} %{vimdir}
    rm -f %{SOURCE0}
    tar -zcf %{SOURCE0} %{vimdir}
    rm -fr %{vimdirsrc} %{vimdir}
    rm -fr %{vimdir}
    cd ../BUILD
fi

rm -fr %{build}
%setup -q -b 0 -n %{vimdir}

%build
cd src
autoconf

sed -e "s+VIMRCLOC  = \$(VIMLOC)+VIMRCLOC = /etc+" Makefile > Makefile.tmp
mv -f Makefile.tmp Makefile

%if %{?rhel}%{!?rhel:0} == 7
%define python3     python3.8m
%define python3conf /opt/rh/rh-python38/root/usr/lib64/python3.8/config-3.8m
%define python3path /opt/rh/rh-python38/root/usr/include/%{python3}
%define python3bin  /opt/rh/rh-python38/root/usr/bin/%{python3}
%endif

%if %{?rhel}%{!?rhel:0} == 8
%define python3     python3.8m
%define python3conf /usr/lib64/python3.8/config-3.8m
%define python3path /usr/include/%{python3}
%define python3bin  /usr/bin/%{python3}
%endif

export CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_FORTIFY_SOURCE=2 -I%{python3path}"
export CXXFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_FORTIFY_SOURCE=2 -I%{python3path}"

%if %{?rhel}%{!?rhel:0} == 7
export LD_LIBRARY_PATH=/opt/rh/rh-python38/root/usr/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
%endif

%configure --with-features=huge \
           --enable-multibyte \
           --enable-python3interp \
           --with-python3-config-dir=%{python3conf} \
           --disable-tclinterp \
           --with-x=no \
           --enable-gui=no \
           --exec-prefix=%{_prefix} \
           --enable-cscope \
           --disable-netbeans \
%if %{with_selinux}
    --enable-selinux \
%else
    --disable-selinux \
%endif
%if "%{with_ruby}" == "1"
    --enable-rubyinterp=%{rubyopt} \
%else
    --disable-rubyinterp \
%endif
%if "%{with_lua}" == "1"
    --enable-luainterp=dynamic \
%else
    --disable-luainterp \
%endif
    --enable-fail-if-missing

make VIMRCLOC=/etc VIMRUNTIMEDIR=/usr/share/vim/%{vimdir} %{?_smp_mflags}


%if %{?rhel}%{!?rhel:0} == 7
cp vim vim8-rhpy38
%endif

%if %{?rhel}%{!?rhel:0} == 8
cp vim vim8-py38
%endif

make clean

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_datadir}/vim/%{vimdir}/{after,autoload,colors,compiler,doc,ftdetect,ftplugin,indent,keymap,lang,plugin,print,spell,syntax,tutor}
mkdir -p %{buildroot}/%{_datadir}/vim/%{vimdir}/after/{autoload,colors,compiler,doc,ftdetect,ftplugin,indent,keymap,lang,plugin,print,spell,syntax,tutor}
cp runtime/doc/uganda.txt LICENSE
rm -f README*.info


cd src
make install DESTDIR=%{buildroot} BINDIR=%{_bindir} VIMRCLOC=/etc VIMRUNTIMEDIR=/usr/share/vim/%{vimdir}
make installgtutorbin  DESTDIR=%{buildroot} BINDIR=%{_bindir} VIMRCLOC=/etc VIMRUNTIMEDIR=/usr/share/vim/%{vimdir}

rm -fr %{buildroot}%{_bindir}/*
rm -fr %{buildroot}%{_datadir}/man
rm -fr %{buildroot}%{_datadir}/icons
rm -fr %{buildroot}%{_datadir}/applications
rm -fr %{buildroot}/%{_datadir}/vim/%{vimdir}/tools
rm -f vim8
ln -sf %{_sysconfdir}/alternatives/vim8 vim8
cp -d vim8 %{buildroot}%{_bindir}/vim8
install -m755 vim8-py38 %{buildroot}%{_bindir}/vim8-py38
%if %{?rhel}%{!?rhel:0} == 7
install -m755 vim8-rhpy38 %{buildroot}%{_bindir}/vim8-rhpy38
%endif

%files
%defattr(-,root,root)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc READMEdir/README*
%{_bindir}/vim8
%if %{?rhel}%{!?rhel:0} == 7
%{_bindir}/vim8-rhpy38
%endif
%{_datadir}/vim/%{vimdir}

%post
if [ $1 == 1 ];then
    # initial install
%if %{?rhel}%{!?rhel:0} == 7
    alternatives --install /usr/bin/vim8 vim8 /usr/bin/vim8-rhpy38 8
%endif
    if [ -f /usr/bin/python3.8m ]; then
        alternatives --set vim8 /usr/bin/vim8-py38
%if %{?rhel}%{!?rhel:0} == 7
    elif [ -f /opt/rh/rh-python38/root/usr/bin/python3.8m ]; then
        alternatives --set vim8 /usr/bin/vim8-rhpy38
%endif
    else
        alternatives --auto vim8
    fi
elif [ $1 == 2 ];then
    echo "upgrading. do nothing"
fi

%postun
if [ $1 == 1 ];then
    echo "upgrading"
elif [ $1 == 0 ];then
    echo "removing"
%if %{?rhel}%{!?rhel:0} == 7
    alternatives --remove vim8 /usr/bin/vim8-rhpy34
%endif
    alternatives --remove vim8 /usr/bin/vim8-py38
fi

%changelog

