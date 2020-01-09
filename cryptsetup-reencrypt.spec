%define fipscheck_version 1.2.0
%define libgcrypt_version 1.4.5
%define device_mapper_version 1.02.61
%define _root_sbindir /sbin
%define enable_fips 0
%define enable_dracut 0
%define dracutmodulesdir %{_datadir}/dracut/modules.d

%if %{enable_fips}
%define fips_string enable
%else
%define fips_string disable
%endif

Summary: A utility for offline reencryption of LUKS encrypted disks.
Name: cryptsetup-reencrypt
Version: 1.6.4
Release: 2%{?dist}
License: GPLv2+ and LGPLv2+
Group: Applications/System
URL: http://cryptsetup.googlecode.com/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libgcrypt-devel >= %{libgcrypt_version}
BuildRequires: device-mapper-devel >= %{device_mapper_version}
BuildRequires: libgpg-error-devel, libuuid-devel, libsepol-devel
BuildRequires: libselinux-devel, popt-devel
%if %{enable_fips}
BuildRequires: fipscheck-devel >= %{fipscheck_version}
%endif
Requires: %{name}-libs = %{version}-%{release}

Source0: https://www.kernel.org/pub/linux/utils/cryptsetup/v1.6/cryptsetup-%{version}.tar.xz

Patch0:  cryptsetup-reencrypt-package-name.patch
Patch1:  cryptsetup-reencrypt-remove-unused-l18n.patch
Patch2:  cryptsetup-1.6.5-reencrypt-fips.patch
Patch3:  cryptsetup-reencrypt-dracut.patch
Patch4:  cryptsetup-1.6.6-use_fsync_instead_odirect_in_log_files.patch
Patch5:  cryptsetup-1.6.8-remove-experimental-warning.patch

%description
This package contains cryptsetup-reencrypt utility which
can be used for offline reencryption of disk in site.
Also includes dracut module required to perform reencryption
of device containing a root filesystem.

%package libs
Group: System Environment/Libraries
Summary: Cryptsetup reencrypt library
Requires: libgcrypt >= %{libgcrypt_version}
%if %{enable_fips}
Requires: fipscheck-lib >= %{fipscheck_version}
%endif

%description libs
This package contains the cryptsetup shared library, libcryptsetup.

%prep
%setup -q -n cryptsetup-%{version}
%patch0 -p1
%patch1 -p1
%if %{enable_fips}
%patch2 -p1
%endif
%if %{enable_dracut}
%patch3 -p1
%endif
%patch4 -p1
%patch5 -p1

%build
%configure --sbindir=%{_root_sbindir} --libdir=/%{_lib} --enable-cryptsetup-reencrypt --disable-veritysetup --disable-kernel_crypto --with-luks1-mode=cbc-essiv:sha256 --%{fips_string}-fips
# remove rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

# Generate HMAC checksums
%if %{enable_fips}
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}} \
  %{__arch_install_post} \
  %{__os_install_post} \
  fipshmac $RPM_BUILD_ROOT/%{_lib}/libcryptsetup.so.*
%endif

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
rm -rf  $RPM_BUILD_ROOT/%{_lib}/*.la $RPM_BUILD_ROOT/%{_lib}/cryptsetup $RPM_BUILD_ROOT/%{_lib}/libcryptsetup.so \
	$RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT/%{_includedir} $RPM_BUILD_ROOT/%{_root_sbindir}/cryptsetup \
	$RPM_BUILD_ROOT/%{_mandir}/man8/cryptsetup.*
%find_lang cryptsetup-reencrypt

%if %{enable_dracut}
install -d -m755 $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt
install -m755 misc/dracut_90reencrypt/install.old $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt/install
install -m755 misc/dracut_90reencrypt/installkernel.old $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt/installkernel
install -m755 misc/dracut_90reencrypt/check.old $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt/check
install -m755 misc/dracut_90reencrypt/parse-reencrypt.sh $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt
install -m755 misc/dracut_90reencrypt/reencrypt.sh $RPM_BUILD_ROOT/%{dracutmodulesdir}/90reencrypt
%endif

%post -n %{name}-libs -p /sbin/ldconfig

%postun -n %{name}-libs -p /sbin/ldconfig

%files
%doc COPYING AUTHORS
%{_mandir}/man8/cryptsetup-reencrypt.8.gz
%{_root_sbindir}/cryptsetup-reencrypt
%if %{enable_dracut}
%{dracutmodulesdir}/90reencrypt
%{dracutmodulesdir}/90reencrypt/*
%endif

%files libs -f cryptsetup-reencrypt.lang
%doc COPYING COPYING.LGPL
/%{_lib}/libcryptsetup.so.*
%if %{enable_fips}
/%{_lib}/.libcryptsetup.so.*.hmac
%endif

%clean

%changelog
* Mon Jan 18 2016 Ondrej Kozina <okozina@redhat.com> - 1.6.4-2
- patch: use fsync instead of O_DIRECT mode while writting reencryption log.
- patch: remove warning phrase while invoking cryptsetup-reencrypt tool.
- Resolves: #1130141 #1140201

* Mon Jun 16 2014 Ondrej Kozina <okozina@redhat.com> - 1.6.4-1
- initial release
