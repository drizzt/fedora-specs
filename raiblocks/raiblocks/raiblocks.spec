# To disable GUI support, specify '--without gui' when building
%bcond_without gui

%define beast_commit		9f10b11eff58aeb793b673c8a8cb6e2bee3db621
%define miniupnp_commit		859b9863854244fdb7eb65f9c185df4e8fe71dc0

%define boost_version		1_63_0
%define boost_components	atomic chrono filesystem log program_options regex system thread

Name:		raiblocks
Version:	7.8.2
Release:	1%{?dist}
Summary:	A low latency, high throughput cryptocurrency

License:	BSD
URL:		https://raiblocks.net/
Source0:	https://github.com/clemahieu/%{name}/archive/V%{version}.tar.gz
Source1:	https://sourceforge.net/projects/boost/files/boost/1.63.0/boost_1_63_0.tar.bz2
Source2:	https://github.com/vinniefalco/Beast/archive/%{beast_commit}.tar.gz
Source3:	https://github.com/miniupnp/miniupnp/archive/%{miniupnp_commit}.tar.gz

Patch0:		no_static_libs.patch
Patch1:		0001-Add-the-possibility-to-build-without-SSE4-support.patch

BuildRequires:	cmake

# For boost
BuildRequires:	python-devel

%if %{with gui}
BuildRequires:	qt5-qtbase-devel
%define additional_cmake_options	-DRAIBLOCKS_GUI:BOOL=ON
%endif

%description
RaiBlocks is designed to be a low latency, high throughput cryptocurrency

We've applied the philosophy of "Do one thing and do it well"
giving you performance and scalability unmatched by any other platform.

RaiBlocks features instant transaction confirmation and has an incredibly
low energy footprint.

%package	wallet
Summary:	Graphical Wallet of RaiBlocks

%description	wallet
Graphical Wallet of RaiBlocks

%package	node
Summary:	Daemon node of RaiBlocks

%description	node
Daemon node of RaiBlocks

%prep
%autosetup -n %{name}-%{version}
%setup -q -T -D -a 1
%setup -q -T -D -a 2
%setup -q -T -D -a 3

rmdir beast
mv -f Beast-%{beast_commit} beast
rmdir miniupnp
mv -f miniupnp-%{miniupnp_commit} miniupnp

%build
cd boost_%{boost_version}

cat > ./tools/build/src/user-config.jam << "EOF"
import os ;
local RPM_OPT_FLAGS = [ os.environ RPM_OPT_FLAGS ] ;

using gcc : : : <compileflags>$(RPM_OPT_FLAGS) ;
EOF

./bootstrap.sh --with-toolset=gcc
./b2 -q %{?_smp_mflags} \
	$( printf -- '--with-%s ' %{boost_components}) \
	--no-samples \
	--no-tests \
	link=static \
	threading=multi	\
	--prefix="$PWD/../boost" \
	install
cd ..

%cmake	\
	-DRAIBLOCKS_WITH_SSE4:BOOL=OFF \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DCMAKE_BUILD_TYPE=Release \
	-DACTIVE_NETWORK=rai_live_network \
	-DBOOST_ROOT="$PWD/boost" \
	%{additional_cmake_options} .
make rai_node rai_wallet %{?_smp_mflags}

%install
mkdir -p %{buildroot}%{_bindir}/
install -m 0755 -t %{buildroot}%{_bindir}/ rai_node rai_wallet

%files
%license LICENSE

%files node
%{_bindir}/rai_node

%files wallet
%{_bindir}/rai_wallet

%changelog
* Wed Mar 08 2017 Timothy Redaelli <tredaelli@redhat.com> - 7.8.2-1
- Initial package
