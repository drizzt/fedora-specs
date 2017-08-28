# To disable GUI support, specify '--without gui' when building
%bcond_without gui

#%%global commit0			32b84a3ccbb9493f2fadfdc60ef6d3cb488f28eb
#%%global date			20170803
#%%global shortcommit0		%(c=%{commit0}; echo ${c:0:7})

%define beast_commit		c7b830f37f8adc0df63d41ff4d31395ab704516b
%define miniupnp_commit		e24d7eca28022b959b331b08e6918b58b303c1cf
%define cryptopp_commit		ed4c345ce86aad98c38fac120569eb9406fbfc37
%define lmdb_commit		60d500206a108b2c64ca7e36b0113b2cd3711b98

%define boost_version		1_63_0
%define boost_components	atomic chrono filesystem log program_options regex system thread

Name:		raiblocks
Version:	8.0
Release:	1%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
Summary:	A low latency, high throughput cryptocurrency

License:	BSD
URL:		https://raiblocks.net/
Source0:	https://github.com/clemahieu/%{name}/archive/%{?commit0}%{?!commit0:V%{version}}.tar.gz#/%{name}-%{?commit0}%{?!shortcommit0:%{version}}.tar.gz
Source1:	https://sourceforge.net/projects/boost/files/boost/1.63.0/boost_1_63_0.tar.bz2
Source2:	https://github.com/vinniefalco/Beast/archive/%{beast_commit}.tar.gz
Source3:	https://github.com/miniupnp/miniupnp/archive/%{miniupnp_commit}.tar.gz
Source4:	https://github.com/weidai11/cryptopp/archive/%{cryptopp_commit}.tar.gz
Source5:	https://github.com/LMDB/lmdb/archive/%{lmdb_commit}.tar.gz

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
%autosetup -n %{name}-%{?commit0}%{?!commit0:%{version}} -p1
%setup -q -T -D -a 1 -n %{name}-%{?commit0}%{?!commit0:%{version}}
%setup -q -T -D -a 2 -n %{name}-%{?commit0}%{?!commit0:%{version}}
%setup -q -T -D -a 3 -n %{name}-%{?commit0}%{?!commit0:%{version}}
%setup -q -T -D -a 4 -n %{name}-%{?commit0}%{?!commit0:%{version}}
%setup -q -T -D -a 5 -n %{name}-%{?commit0}%{?!commit0:%{version}}

rmdir beast
mv -f beast-%{beast_commit} beast
rmdir miniupnp
mv -f miniupnp-%{miniupnp_commit} miniupnp
rmdir cryptopp
mv -f cryptopp-%{cryptopp_commit} cryptopp
rmdir lmdb
mv -f lmdb-%{lmdb_commit} lmdb

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
