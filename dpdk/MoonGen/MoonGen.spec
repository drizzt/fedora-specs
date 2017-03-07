# snapshot is the date YYYYMMDD of the snapshot
# snap_git is the 8 git sha digits of the last commit
# Use moongen-snapshot.sh to create the tarball.
%global		snapshot	20170124
%global		snap_git	ef3aa3f7

Name:		MoonGen
Version:	0
Release:	1.%{snapshot}.%{snap_git}%{?dist}
Summary:	high-speed packet generator built on DPDK and LuaJIT

#Group:		
License:	MIT
URL:		https://github.com/emmericp/MoonGen
Source0:	%{name}-%{snap_git}.tar.gz
Source1:	moongen-snapshot.sh

# Fix lua path (needs to be fixed and sent upstream)
Patch0:         fix-lua-path.patch
# Remove kni support (consider to send a conditional patch upstream)
Patch2:         libmoon-remove-kni.patch
# Fix for kernel 4.8 and kernel 4.9
Patch3:		https://github.com/emmericp/dpdk/commit/570ac8b27a27e7c5163ef2cd96984078007fac52.patch

BuildRequires:  cmake

%define dpdk_machine native
%define dpdk_target x86_64-%{dpdk_machine}-linuxapp-gcc

%description
MoonGen is a fully scriptable high-speed packet generator built on DPDK and LuaJIT.
It can saturate a 10 Gbit/s connection with 64 byte packets on a single CPU core
while executing user-provided Lua scripts for each packet.
Multi-core support allows for even higher rates.
It also features precise and accurate timestamping and rate control. 

%prep
%setup -n %name-%snap_git
%patch0 -p1
cd libmoon
%patch2 -p1
cd deps/dpdk
%patch3 -p1

%build
function setconf()
{
    cf=%{dpdk_target}/.config
    if grep -q ^$1= $cf; then
        sed -i "s:^$1=.*$:$1=$2:g" $cf
    else
        echo $1=$2 >> $cf
    fi
}
# In case dpdk-devel is installed
unset RTE_SDK RTE_INCLUDE RTE_TARGET

# See build.sh
cd libmoon/deps/luajit
make %{?_smp_mflags} BUILDMODE=static 'CFLAGS+=-DLUAJIT_NUMMODE=2 -DLUAJIT_ENABLE_LUA52COMPAT'
make install DESTDIR=$(pwd)
cd ->/dev/null

cd libmoon/deps/dpdk
make V=1 O=%{dpdk_target} T=%{dpdk_target} %{?_smp_mflags} config

# Disable kernel modules
setconf CONFIG_RTE_EAL_IGB_UIO n
setconf CONFIG_RTE_LIBRTE_KNI n
setconf CONFIG_RTE_KNI_KMOD n

make V=1 O=%{dpdk_target} %{?_smp_mflags}
cd ->/dev/null

cd build
%cmake -DCMAKE_SKIP_RPATH:BOOL=ON ..
make %{?_smp_mflags}

%install
install -m 755 -d %{buildroot}/%{_bindir}
install -m 755 -D build/%{name} %{buildroot}/%{_bindir}/%{name}
install -m 755 -d %{buildroot}/%{_datadir}/%{name}/lua
cp -r lua/* libmoon/lua/* %{buildroot}/%{_datadir}/%{name}/lua

%check
ctest -V %{?_smp_mflags}

%files
%license LICENSE
%doc README.md examples
%{_datadir}/%{name}/lua
%{_bindir}/%{name}

%changelog
* Tue Mar 07 2017 Timothy Redaelli <tredaelli@redhat.com> - 0-1.20170124.ef3aa3f7
- Initial package
