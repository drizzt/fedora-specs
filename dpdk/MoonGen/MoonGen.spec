# snapshot is the date YYYYMMDD of the snapshot
# snap_git is the 8 git sha digits of the last commit
# Use moongen-snapshot.sh to create the tarball.
%global		snapshot	20170124
%global		snap_git	ef3aa3f7

Name:		MoonGen
Version:	0
Release:	1.%{snapshot}.%{snap_git}%{?dist}
Summary:	High-speed packet generator built on DPDK and LuaJIT

#Group:		
License:	MIT
URL:		https://github.com/emmericp/MoonGen
Source0:	%{name}-%{snap_git}.tar.gz
Source1:	moongen-snapshot.sh

## Patches for MoonGen
# Fix lua path (needs to be fixed and sent upstream)
Patch0:		fix-lua-path.patch

## Patches for MoonGen/libmoon
# Remove kni support (consider to send a conditional patch upstream)
Patch10:	libmoon-remove-kni.patch
# add support for libjemalloc.so.2
Patch11:	https://github.com/libmoon/libmoon/commit/86b401bcd17bb9124d1cc6a2dd13aec45c00da1c.patch

BuildRequires:	cmake
Requires:	jemalloc

ExclusiveArch:	x86_64

%define dpdk_machine native
%define dpdk_target x86_64-%{dpdk_machine}-linuxapp-gcc

%description
MoonGen is a fully scriptable high-speed packet generator built on
DPDK and LuaJIT.
It can saturate a 10 Gbit/s connection with 64 byte packets on a single CPU
core while executing user-provided Lua scripts for each packet.
Multi-core support allows for even higher rates.
It also features precise and accurate timestamping and rate control. 

%prep
%setup -q -n %name-%snap_git
%patch0 -p1
cd libmoon
%patch10 -p1
%patch11 -p1

%build
setconf()
{
	cf=%{dpdk_target}/.config
	if grep -q "^$1=" $cf; then
		sed -i "s:^$1=.*$:$1=$2:g" $cf
	else
		echo "$1=$2" >> $cf
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
install -m 755 -d %{buildroot}/%{_datadir}/%{name}/deps/pciids
install -m 644 -D libmoon/deps/pciids/pci.ids \
	%{buildroot}/%{_datadir}/%{name}/deps/pciids

install -m 755 -d %{buildroot}/%{_datadir}/%{name}/lua
cp -r lua/* libmoon/lua/* %{buildroot}/%{_datadir}/%{name}/lua

install -m 755 -d %{buildroot}/%{_bindir}
install -m 755 -D build/%{name} %{buildroot}/%{_bindir}/%{name}

%check
ctest -V %{?_smp_mflags}

%files
%license LICENSE
%doc README.md examples
%{_datadir}/%{name}/deps/pciids/pci.ids
%{_datadir}/%{name}/lua
%{_bindir}/%{name}

%changelog
* Tue Mar 07 2017 Timothy Redaelli <tredaelli@redhat.com> - 0-1.20170124.ef3aa3f7
- Initial package
