%define luaver 5.3.4

Name:		pktgen-dpdk
Version:	3.4.8
Release:	0%{?dist}
Summary:	Traffic generator utilizing DPDK

Group:		Applications/Internet
License:	BSD (??)
URL:		https://github.com/Pktgen/Pktgen-DPDK/
Source:	        http://dpdk.org/browse/apps/pktgen-dpdk/snapshot/pktgen-%{version}.tar.gz
Source1:        https://www.lua.org/ftp/lua-%{luaver}.tar.gz

BuildRequires:	dpdk-devel >= 16.04
# bogus deps due to makefile confusion over static linkage and whatnot
BuildRequires:	libpcap-devel zlib-devel numactl-devel
BuildRequires:	openssl-devel

BuildRequires:  python-sphinx

# The tarball contains two bundled 'n hacked up Lua versions, sigh.
# There are at least two additions to upstream: lua_shell and lua-socket
# so a simple rm -rf of the directory wont cut it. Needs to be
# unbundled or exception requested.
# This is the one that gets built and statically linked in the binary:
Provides:	bundled(lua) = %{luaver}
# It also conflicts with system-wide installation of lua-devel, sigh.
BuildConflicts: lua-devel

%description
%{summary}

%prep
%autosetup -n pktgen-%{version} -p1

%build
unset RTE_SDK
. /etc/profile.d/dpdk-sdk-%{_arch}.sh

ln -s %{SOURCE1} lib/lua
make -C lib/lua get_tarball

# Hack up Lua library path to our private libdir
sed -ie 's:/usr/local:%{_libdir}:g' lib/lua/lua-%{luaver}/src/luaconf.h
sed -ie 's:share/lua/.*:/%{name}/":g' lib/lua/lua-%{luaver}/src/luaconf.h
sed -ie 's:lib/lua/.*:/%{name}/":g' lib/lua/lua-%{luaver}/src/luaconf.h

# Doesn't build with the default -Werror, sigh...
export EXTRA_CFLAGS="$(echo %{optflags} -Wno-error | sed -e 's:-march=[[:alnum:]]* ::g')"

# Parallel build doesn't work
# Work around DPDK makefiles, we're not building shared libraries here
# make V=1 %{?_smp_mflags}
make V=1 CONFIG_RTE_BUILD_SHARED_LIB=n

make -C docs/ V=1 man

%install
unset RTE_SDK
. /etc/profile.d/dpdk-sdk-%{_arch}.sh
# No working "install" target, lets do it manually (sigh)
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_mandir}/%{name}/man1
if [ -f app/${RTE_TARGET}/pktgen ]; then
  install -m 755 app/${RTE_TARGET}/pktgen %{buildroot}%{_bindir}/pktgen
else
  install -m 755 app/app/${RTE_TARGET}/pktgen %{buildroot}%{_bindir}/pktgen
fi
for f in Pktgen.lua PktgenGUI.lua; do
   install -m 644 ${f} %{buildroot}%{_libdir}/%{name}/${f}
done
install -m 644 docs/build/man/pktgen.1 %{buildroot}%{_mandir}/%{name}/man1/pktgen.1

%files
%license LICENSE
%doc README.md
%doc pcap themes test
%{_bindir}/pktgen
%{_libdir}/%{name}
%{_mandir}/%{name}

%changelog
* Fri Jan 12 2018 Timothy Redaelli <tredaelli@redhat.com> - 3.4.8-0
- Update to 3.4.8 linked with DPDK 17.11

* Fri Nov 17 2017 Timothy Redaelli <tredaelli@redhat.com> - 3.4.2-0.1
- Update to 3.4.2 linked with DPDK 17.11

* Fri Jul 28 2017 Timothy Redaelli <tredaelli@redhat.com> - 3.3.8-0
- Update to 3.3.8
- Build manpage

* Fri Mar 03 2017 Flavio Leitner <fbl@redhat.com> - 3.1.2-1
- Update to 3.1.2

* Mon Jan 23 2017 Timothy Redaelli <tredaelli@redhat.com> 3.1.0-1
- Update to 3.1.0
- Bundled lua version is 5.3.3

* Thu Aug 18 2016 Panu Matilainen <pmatilai@redhat.com> - 3.0.12-1
- Update to 3.0.12
- Source name changing yet again, flip-flop SIGH

* Wed Aug 03 2016 Panu Matilainen <pmatilai@redhat.com> - 3.0.09-1
- Update to 3.0.09
- Source name changing yet again, sigh
- Buildrequire openssl-devel

* Thu Apr 28 2016 Panu Matilainen <pmatilai@redhat.com> - 3.0.02-1
- Update to 3.0.02

* Thu Apr 28 2016 Panu Matilainen <pmatilai@redhat.com> - 3.0.0-1
- Update to 3.0.0

* Tue Apr 12 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.16-1
- Update to 2.9.16

* Mon Apr 04 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.13-1
- Update to 2.9.13

* Wed Mar 30 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-6
- Bump + rebuild

* Fri Mar 11 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-5
- Hack -march out of rpm optflags to permit build on i686

* Fri Mar 11 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-4
- Bump + rebuild for new arch

* Thu Mar 10 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-3
- Bump + rebuild for ABI changes

* Mon Feb 22 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-2
- Bump + rebuild

* Tue Feb 16 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.12-1
- Update to 2.9.12

* Wed Jan 20 2016 Panu Matilainen <pmatilai@redhat.com> - 2.9.8-1
- Update to 2.9.8
- Bump DPDK requirement to 2.1

* Wed Dec 16 2015 Panu Matilainen <pmatilai@redhat.com> - 2.9.7-1
- Update to 2.9.7
- Build conflicts with lua-devel, sigh

* Mon Sep 28 2015 Panu Matilainen <pmatilai@redhat.com> - 2.9.2-2
- Rebuild for dpdk changes
- Buildrequires zlib-devel (static linking brokenness carried over
  to shared libraries, sigh)

* Mon Sep 28 2015 Panu Matilainen <pmatilai@redhat.com> - 2.9.2-1
- Update to 2.9.2
- Drop bogus fuse-devel buildreq

* Fri Mar 27 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.4-1
- Update to 2.8.4

* Mon Mar 02 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.3-1
- Update to 2.8.3
- Use rpm optflags for building

* Fri Feb 27 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-6
- Rebuild

* Tue Feb 17 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-5
- Add some missing Lua bits and pieces
- Workaround DPDK linking madness by buildrequiring fuse-devel

* Thu Feb 05 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-4
- Another rebuild for versioning change

* Thu Feb 05 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-3
- Another rebuild for versioning change

* Tue Feb 03 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-2
- Rebuild with library versioned dpdk
- Ensure RTE_SDK from dpdk-devel gets used

* Fri Jan 30 2015 Panu Matilainen <pmatilai@redhat.com> - 2.8.0-1
- Initial packaging

