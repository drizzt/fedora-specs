# snapshot is the date YYYYMMDD of the snapshot
# snap_git is the 8 git sha digits of the last commit
# Use moongen-snapshot.sh to create the tarball.
%global		snapshot	20170124
%global		snap_git	ef3aa3f7

Name:		MoonGen
Version:	0
Release:	2.%{snapshot}.%{snap_git}%{?dist}
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
# Try to use system pci.ids if deps/pciids/pci.ids is not available
Patch12:	https://patch-diff.githubusercontent.com/raw/libmoon/libmoon/pull/26.patch

BuildRequires:	cmake
BuildRequires:	luajit-devel >= 2.1.0
Requires:	jemalloc
Requires:	hwdata
# Upstream didn't change ABI version
Requires:	luajit >= 2.1.0

# FIXME Avoid static linking of DPDK
# Ripped from dpdk.spec (16.07-1)
#
# The DPDK is designed to optimize througput of network traffic using, among
# other techniques, carefully crafted x86 assembly instructions.  As such it
# currently (and likely never will) run on non-x86 platforms
#
ExclusiveArch: x86_64 i686

# machine_arch maps between rpm and dpdk arch name, often same as _target_cpu
%define machine_arch %{_target_cpu}
# machine_tmpl is the config template machine name, often "native"
%define machine_tmpl native
# machine is the actual machine name used in the dpdk make system
%ifarch x86_64
%define machine default
%endif
%ifarch i686
%define machine atm
%endif

%define target %{machine_arch}-%{machine_tmpl}-linuxapp-gcc

%define pmddir %{_libdir}/dpdk-pmds

# End "Ripped from dpdk.spec"

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
sed -i 's/x86_64-native-linuxapp-gcc/%{target}/g' CMakeLists.txt libmoon/CMakeLists.txt

cd libmoon
%patch10 -p1
%patch11 -p1
%patch12 -p1

%build
# FIXME Avoid static linking of DPDK
cd libmoon/deps/dpdk
# Partially ripped from dpdk.spec (16.07)
# set up a method for modifying the resulting .config file
function setconf() {
	if grep -q ^$1= %{target}/.config; then
		sed -i "s:^$1=.*$:$1=$2:g" %{target}/.config
	else
		echo $1=$2 >> %{target}/.config
	fi
}

# In case dpdk-devel is installed, we should ignore its hints about the SDK directories
unset RTE_SDK RTE_INCLUDE RTE_TARGET

# Avoid appending second -Wall to everything, it breaks upstream warning
# disablers in makefiles. Strip expclit -march= from optflags since they
# will only guarantee build failures, DPDK is picky with that.
export EXTRA_CFLAGS="$(echo %{optflags} | sed -e 's:-Wall::g' -e 's:-march=[[:alnum:]]* ::g') -Wformat -fPIC"

# DPDK defaults to using builder-specific compiler flags.  However,
# the config has been changed by specifying CONFIG_RTE_MACHINE=default
# in order to build for a more generic host.  NOTE: It is possible that
# the compiler flags used still won't work for all Fedora-supported
# machines, but runtime checks in DPDK will catch those situations.

make V=1 O=%{target} T=%{target} config

setconf CONFIG_RTE_MACHINE '"%{machine}"'
# Disable experimental features
setconf CONFIG_RTE_NEXT_ABI n
setconf CONFIG_RTE_LIBRTE_CRYPTODEV n
setconf CONFIG_RTE_LIBRTE_MBUF_OFFLOAD n

setconf CONFIG_RTE_EAL_IGB_UIO n
setconf CONFIG_RTE_LIBRTE_KNI n
setconf CONFIG_RTE_KNI_KMOD n
setconf CONFIG_RTE_KNI_PREEMPT_DEFAULT n

make V=1 O=%{target}

# End "Partially ripped from dpdk.spec (16.07)"

cd ->/dev/null

cd build
%cmake -DCMAKE_SKIP_RPATH:BOOL=ON ..
make %{?_smp_mflags}

%install
install -m 755 -d %{buildroot}/%{_datadir}/%{name}/lua
cp -r lua/* libmoon/lua/* %{buildroot}/%{_datadir}/%{name}/lua

install -m 755 -d %{buildroot}/%{_bindir}
install -m 755 -D build/%{name} %{buildroot}/%{_bindir}/%{name}

%check
ctest -V %{?_smp_mflags}

%files
%license LICENSE
%doc README.md examples
%{_datadir}/%{name}/lua
%{_bindir}/%{name}

%changelog
* Tue Mar 14 2017 Timothy Redaelli <tredaelli@redhat.com> - 0-2.20170124.ef3aa3f7
- Build only for i686 and x86_64
- Use configuration from upstream Fedora dpdk.spec
- Do not statically link with LuaJIT
- Use /usr/share/hwdata/pci.ids
- Build DPDK without specifying -j (sometimes it doesn't work correctly)

* Tue Mar 07 2017 Timothy Redaelli <tredaelli@redhat.com> - 0-1.20170124.ef3aa3f7
- Initial package
