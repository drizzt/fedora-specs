%global		pyzmq_version	14.5.0

Name:		trex-core
Version:	2.30
Release:	0.4%{?dist}
Summary:	TRex Low-Cost, High-Speed Stateful Traffic Generator - Core

License:	ASL 2.0
URL:		https://trex-tgn.cisco.com/
Source0:	https://github.com/cisco-system-traffic-generator/trex-core/archive/v%version.tar.gz#/%name-%version.tar.gz
Source1:	https://pypi.io/packages/source/p/pyzmq/pyzmq-%{pyzmq_version}.tar.gz

Patch0:		0001-linux_dpdk-Use-system-zmq-library.patch
Patch1:		fix-paths.patch

BuildRequires:	chrpath
BuildRequires:	zlib-devel zeromq-devel
BuildRequires:	python2-devel
Requires:       pciutils

# FIXME Actually trex-core embeds a specific version of openssl
AutoReqProv:	no
Requires:	bash python2 zeromq

# FIXME Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global debug_package %{nil}

%global targets _t-rex-64,_t-rex-64-o

%description
%summary


%prep
%autosetup -p1 -a1


%build
# Build pyzmq
pushd pyzmq-%{pyzmq_version}
python setup.py clean -a
python setup.py build --zmq=bundled
popd
rm -rf scripts/external_libs/pyzmq-%{pyzmq_version}
mkdir -p scripts/external_libs/pyzmq-%{pyzmq_version}/python2/ucs4/64bit/
mv pyzmq-%{pyzmq_version}/build/lib.linux-*/zmq scripts/external_libs/pyzmq-%{pyzmq_version}/python2/ucs4/64bit/

# FIXME
export CFLAGS="%{optflags} -Wno-error=format-security -Wno-format-security"
export CXXFLAGS="%{optflags} -Wno-error=format-security -Wno-format-security"
export LINKFLAGS="%{__global_ldflags}"
sed -i "s/'-Werror',//" linux{,_dpdk}/ws_main.py

pushd linux
./b --targets=bp-sim-64 \
    configure -v \
    --prefix=%{_prefix} \
    --libdir=%{_libdir}

./b --targets=bp-sim-64 \
    build -v %{?_smp_mflags}
popd

pushd linux_dpdk
./b --targets=%{targets} \
    configure -v \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --no-mlx

./b --targets=%{targets} \
    build -v %{?_smp_mflags}
popd

%install
pushd linux
./b --targets=bp-sim-64 \
    install --destdir=%{buildroot}
popd

pushd linux_dpdk
./b --targets=%{targets} \
    install --destdir=%{buildroot}
popd

# Get rid of rpaths
chrpath --delete %{buildroot}%{_bindir}/*

# FIXME sadly upstream likes to have all the stuff in one directory :(
# Install stuff
mkdir -p %{buildroot}%{_datadir}/%{name}/scripts
for x in trex-cfg stl-sim astf-sim find_python.sh run_regression \
         run_functional_tests dpdk_nic_bind.py dpdk_setup_ports.py \
         doc_process.py trex_daemon_server scapy_daemon_server \
         master_daemon.py trex-console daemon_server t-rex-64; do
         
         install -m755 scripts/$x %{buildroot}%{_datadir}/%{name}/scripts/$x
done
for x in cap2 avl cfg external_libs python-lib stl exp astf automation ko; do
    cp -r scripts/$x %{buildroot}%{_datadir}/%{name}/scripts/
done
ln -s t-rex-64 %{buildroot}%{_datadir}/%{name}/scripts/t-rex-64-o
ln -s %{_datadir}/%{name}/scripts/t-rex-64 %{buildroot}%{_bindir}/t-rex-64
ln -s %{_datadir}/%{name}/scripts/t-rex-64-o %{buildroot}%{_bindir}/t-rex-64-o

# Get rid of other rpaths
chrpath --delete %{buildroot}%{_datadir}/%{name}/scripts/automation/phantom/phantomjs

%files
%license LICENSE
%{_bindir}/bp-sim-64
%{_bindir}/_t-rex-64
%{_bindir}/_t-rex-64-o
%{_bindir}/t-rex-64
%{_bindir}/t-rex-64-o
%{_libdir}/libbpf-64.so
%{_libdir}/libbpf-64-o.so
%{_datadir}/%{name}/scripts/*


%changelog
* Wed Oct 04 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.30-0.4
- Initial version, still needs improvements and fixmes

