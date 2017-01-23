Name:           btchip-udev
Version:        1.0
Release:        1%{?dist}
Summary:        Udev rules to connect BTChip wallet to your Linux box

License:        Public Domain
URL:            https://www.ledgerwallet.com/
Source0:        71-hw1.rules
BuildArch:      noarch
BuildRequires:  udev

%description
Udev rules to connect BTChip wallet to your linux box.

%install
mkdir -p %{buildroot}/%{_udevrulesdir}
install -p -m 755 %{SOURCE0} %{buildroot}/%{_udevrulesdir}

%files
%{_udevrulesdir}/71-hw1.rules


%changelog
* Mon Jan 23 2017 Timothy Redaelli <tredaelli@redhat.com> 1.0-1
- new package built with tito

