%define frr_uid  92
%define frr_gid  92
%define vty_group   frrvt
%define vty_gid     85

%global _hardened_build 1

Name: frr
Version: 2.0
Release: 0.1%{?dist}
Summary: Routing daemon
License: GPLv2+
Group: System Environment/Daemons
URL: http://www.frr.net
Source0: https://github.com/FRRouting/frr/releases/download/frr-2.0/%{name}-%{version}.tar.xz
Source1: frr-filter-perl-requires.sh
Source2: frr-tmpfs.conf
BuildRequires: perl-generators pkgconfig
BuildRequires: systemd-devel
BuildRequires: net-snmp-devel
BuildRequires: texinfo libcap-devel texi2html
BuildRequires: readline readline-devel ncurses ncurses-devel
BuildRequires: git
BuildRequires: c-ares-devel json-c-devel python-devel
Requires: net-snmp ncurses c-ares
Requires: python python-ipaddr
Requires(post): systemd /sbin/install-info
Requires(preun): systemd /sbin/install-info
Requires(postun): systemd
Provides: routingdaemon = %{version}-%{release}
Obsoletes: quagga bird gated mrt zebra frr-sysvinit

%define __perl_requires %{SOURCE1}

%description
FRRouting is a free software that manages TCP/IP based routing
protocol. It takes multi-server and multi-thread approach to resolve
the current complexity of the Internet.

FRRouting supports BGP4, OSPFv2, OSPFv3, ISIS, RIP, RIPng, PIM
and LDP

FRRouting is a fork of Quagga.

%package contrib
Summary: Contrib tools for frr
Group: System Environment/Daemons

%description contrib
Contributed/3rd party tools which may be of use with frr.

%package devel
Summary: Header and object files for frr development
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}

%description devel
The frr-devel package contains the header and object files necessary for
developing OSPF-API and frr applications.

%prep
%autosetup -S git_am

%build
%configure \
    --sysconfdir=%{_sysconfdir}/frr \
    --libdir=%{_libdir}/frr \
    --libexecdir=%{_libexecdir}/frr \
    --localstatedir=%{_localstatedir}/run/frr \
    --sbindir=%{_prefix}/lib/frr \
    --enable-ipv6=yes \
    --enable-isisd=yes \
    --enable-snmp=agentx \
    --enable-multipath=64 \
    --enable-opaque-lsa \
    --enable-ospf-te \
    --enable-vtysh=yes \
    --enable-ospfclient=no \
    --enable-ospfapi=no \
    --enable-user=frr \
    --enable-group=frr \
    --enable-vty-group=%vty_group \
    --enable-rtadv \
    --disable-exampledir \
    --enable-netlink \
    --enable-nhrpd \
    --enable-systemd=yes \
    --enable-pool=yes

make %{?_smp_mflags} MAKEINFO="makeinfo --no-split" CFLAGS="%{optflags} -fno-strict-aliasing"

pushd doc
texi2html frr.texi
popd

%install
mkdir -p %{buildroot}/etc/{frr,rc.d/init.d,default,logrotate.d,pam.d} \
         %{buildroot}/var/log/frr %{buildroot}%{_infodir} \
         %{buildroot}%{_unitdir}

make DESTDIR=%{buildroot} INSTALL="install -p" CP="cp -p" install

# Remove this file, as it is uninstalled and causes errors when building on RH9
rm -rf %{buildroot}/usr/share/info/dir

install -p -m 644 %{_builddir}/%{name}-%{version}/cumulus/etc/frr/debian.conf %{buildroot}/etc/frr
install -p -m 644 %{_builddir}/%{name}-%{version}/cumulus/etc/frr/daemons %{buildroot}/etc/frr
install -p -m 644 %{_builddir}/%{name}-%{version}/tools/frr.service %{buildroot}%{_unitdir}/frr.service
install -p -m 644 %{_builddir}/%{name}-%{version}/redhat/frr.sysconfig %{buildroot}/etc/default/frr
install -p -m 644 %{_builddir}/%{name}-%{version}/redhat/frr.logrotate %{buildroot}/etc/logrotate.d/frr
install -p -m 644 %{_builddir}/%{name}-%{version}/redhat/frr.pam %{buildroot}/etc/pam.d/frr

install -d -m 770  %{buildroot}/var/run/frr

install -d -m 755 %{buildroot}/%{_tmpfilesdir}
install -p -m 644 %{SOURCE2} %{buildroot}/%{_tmpfilesdir}/frr.conf

rm %{buildroot}%{_libdir}/frr/*.a
rm %{buildroot}%{_libdir}/frr/*.la

%pre
getent group %vty_group >/dev/null 2>&1 || groupadd -r -g %vty_gid %vty_group >/dev/null 2>&1 || :
getent group frr >/dev/null 2>&1 || groupadd -g %frr_gid frr >/dev/null 2>&1 || :
getent passwd frr >/dev/null 2>&1 || useradd -u %frr_uid -g %frr_gid -M -r -s /sbin/nologin \
 -c "frr routing suite" -d %{_localstatedir}/run/frr frr >/dev/null 2>&1 || :
usermod -a -G %vty_group frr

%post
%systemd_post frr.service

if [ -f %{_infodir}/%{name}.inf* ]; then
    install-info %{_infodir}/frr.info %{_infodir}/dir || :
fi

# Create dummy files if they don't exist so basic functions can be used.
if [ ! -e %{_sysconfdir}/frr/zebra.conf ]; then
    echo "hostname `hostname`" > %{_sysconfdir}/frr/zebra.conf
    chown frr:frr %{_sysconfdir}/frr/zebra.conf
    chmod 640 %{_sysconfdir}/frr/zebra.conf
fi

if [ ! -e %{_sysconfdir}/frr/vtysh.conf ]; then
    touch %{_sysconfdir}/frr/vtysh.conf
    chmod 640 %{_sysconfdir}/frr/vtysh.conf
    chown frr:%{vty_group} %{_sysconfdir}/frr/vtysh.conf
fi

%postun
%systemd_postun_with_restart frr.service

if [ -f %{_infodir}/%{name}.inf* ]; then
    install-info --delete %{_infodir}/frr.info %{_infodir}/dir || :
fi

%preun
%systemd_preun frr.service

%files
%defattr(-,root,root)
%doc AUTHORS COPYING
%doc zebra/zebra.conf.sample
%doc isisd/isisd.conf.sample
%doc ripd/ripd.conf.sample
%doc bgpd/bgpd.conf.sample*
%doc ospfd/ospfd.conf.sample
%doc ospf6d/ospf6d.conf.sample
%doc ripngd/ripngd.conf.sample
%doc doc/frr.html
%doc doc/mpls
%doc ChangeLog INSTALL NEWS README REPORTING-BUGS SERVICES
%dir %attr(750,frr,frr) %{_sysconfdir}/frr
%dir %attr(750,frr,frr) /var/log/frr
%dir %attr(750,frr,frr) /var/run/frr
%{_infodir}/*info*
%{_mandir}/man*/*
%{_prefix}/lib/frr/*
%{_bindir}/*
%dir %{_libdir}/frr
%{_libdir}/frr/*.so.*
%config /etc/frr/[!v]*
%config(noreplace) %attr(640,root,root) /etc/logrotate.d/frr
%config(noreplace) /etc/default/frr
%config(noreplace) /etc/pam.d/frr
%{_tmpfilesdir}/frr.conf
%{_unitdir}/frr.service

%files contrib
%defattr(-,root,root)
%doc AUTHORS COPYING %attr(0644,root,root) tools

%files devel
%defattr(-,root,root)
%doc AUTHORS COPYING
%dir %{_libdir}/frr/
%{_libdir}/frr/*.so
%dir %{_includedir}/frr
%{_includedir}/frr/*.h
%dir %{_includedir}/frr/ospfd
%{_includedir}/frr/ospfd/*.h

%changelog
* Wed May 31 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.0-0.1
- Initial version (highly based on Fedora quagga package)

