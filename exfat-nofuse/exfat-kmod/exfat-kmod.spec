%global commit0 97f9e2d6259aa0820d23c7259aac50467d208a32
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod

Name: exfat-kmod
Version: 0
Release: 1.git%{shortcommit0}%{?dist}
Summary: Akmod package for kernel mode EXFAT module

License: GPL
URL: https://github.com/dorimanx/exfat-nofuse
Source0: https://github.com/dorimanx/exfat-nofuse/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: %{_bindir}/kmodtool
Provides: exfat-kmod-common

# Disable the building of the debug package(s).
%define debug_package %{nil}

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Akmod package for kernel mode EXFAT module

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T -a 0

for kernel_version in %{?kernel_versions} ; do
    cp -a exfat-nofuse-%{commit0} _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS=${PWD}/_kmod_build_${kernel_version%%___*} CONFIG_EXFAT_FS=m modules
done

%install
rm -rf ${RPM_BUILD_ROOT}

for kernel_version in %{?kernel_versions}; do
    ls _kmod_build_${kernel_version%%___*}/
    mkdir -p  $RPM_BUILD_ROOT/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    %{__install} -D -m 0755 _kmod_build_${kernel_version%%___*}/exfat.ko \
        $RPM_BUILD_ROOT/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}

%clean
rm -rf $RPM_BUILD_ROOT

%package -n exfat-kmod-common
Summary: Dummy package

%description  -n exfat-kmod-common
Dummy package

%files -n exfat-kmod-common

%changelog
* Mon Feb  8 2016 Dick Marinus
- initial version
