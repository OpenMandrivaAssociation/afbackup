%define cryptkey afbackup
%define clientconf afclient.conf
%define serverconf afserver.conf
%define confdir %{_sysconfdir}/afbackup
%define bindir %{_sbindir}
%define logdir %{_var}/log/afbackup
%define vardir %{_var}/lib/afbackup
%define commondir %{_libdir}/afbackup
%define rexecdir %{_libexecdir}/afbackup
%define libdir %{confdir}

Summary:	Client-server backup system
Name:		afbackup
Version:	3.5.3
Release:	7
License:	GPL
Group:		Archiving/Backup
Url:		https://afbackup.sf.net
Source0:	%{name}-%{version}.tar.gz
Source1:	afbackup-xinetd.afbackup
Source3:	afbackup-afmbackup-rc
Source100:	%{name}.rpmlintrc
Patch0:		afbackup-3.3.6-configs.patch
#patch1 sent upstream (Kharec)
Patch1:		afbackup-3.5.3-fix-str-fmt.patch
Requires:	sharutils
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)

%description
Client-Server Backup System
This is a client-server backup system offering several workstations a
centralized backup to a special backup server. Backing up only one
computer is easily possible, too. Any streaming device can be used
for writing the data to it, usually this will be a tape
device. Writing backups is normally done sequentially: The next
writing to tape goes to the end of the previous write no matter where
you have restored from in the meantime. This package is for server or
client with remote-start.

Features:
 - Authentication of the client is performed before it can take over control 
 - Access restriction for the streamer device -> security
 - Client-side per-file compression -> reliability
 - Data stream is written to tape in pieces -> fast finding of files 
 - Tape position logging for each file
 - Tape capacity is fully used
 - Full / incremental backups
 - Raw partitions can be backuped
 - Client and Server buffering for maximal throughput is done
 - DES authentication support

Documentation:
http://afbackup-doc.sourceforge.net/html/

%package client
Summary:	AF's backup system client
Group:		Archiving/Backup
Requires:	sharutils

%description client
Client-Server Backup System (Client side)
This is a client-server backup system offering several workstations a
centralized backup to a special backup server. Backing up only one
computer is easily possible, too. Any streaming device can be used
for writing the data to it, usually this will be a tape
device. Writing backups is normally done sequentially: The next
writing to tape goes to the end of the previous write no matter where
you have restored from in the meantime. This is only the client, you
need to have a server running on either this or another host.

Features:
 - Authentication of the client is performed before it can take over control
 - Access restriction for the streamer device -> security
 - Client-side per-file compression -> reliability
 - Data stream is written to tape in pieces -> fast finding of files
 - Tape position logging for each file
 - Tape capacity is fully used
 - Full / incremental backups
 - Raw partitions can be backuped
 - Client and Server buffering for maximal throughput is done
 - DES authentication support

Documentation:
http://afbackup-doc.sourceforge.net/html/

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1 -b .cfg
%patch1 -p0 -b .str

%build
%configure2_5x --without-prefixext \
    --with-clientbindir=%{bindir} \
    --with-clientconf=%{clientconf} \
    --with-clientconfdir=%{confdir} \
    --with-clientlibdir=%{libdir} \
    --with-clientlogdir=%{logdir} \
    --with-clientmandir=%{_mandir} \
    --with-clientvardir=%{vardir} \
    --with-commondir=%{commondir} \
    --with-commondatadir=%{commondir} \
    --with-commonshlibdir=%{commondir} \
    --with-rexecdir=%{rexecdir} \
    --with-serverbindir=%{bindir} \
    --with-serverconf=%{serverconf} \
    --with-serverconfdir=%{confdir} \
    --with-serverlibdir=%{libdir} \
    --with-serverlogdir=%{logdir} \
    --with-servermandir=%{_mandir} \
    --with-servervardir=%{vardir} \
    --with-zlib \
    --disable-nls \
    --sysconfdir=%{confdir} \
    --with-des --with-des-ldflag=-lcrypto --with-des-include=/usr/include/openssl

echo %{cryptkey} | make all OPTIMIZE="%{optflags}"

%install
mkdir -p %{buildroot}%{_mandir}/man8
mkdir -p %{buildroot}%{logdir}
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
mkdir -p %{buildroot}%{_initrddir}
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/xinetd.d/afbackup-xinetd
install -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/afbackup
make install.client install.server \
    SERVERBINDIR=%{buildroot}%{bindir} \
    SERVERCONFDIR=%{buildroot}%{confdir} \
    SERVERLIBDIR=%{buildroot}%{libdir} \
    SERVERVARDIR=%{buildroot}%{vardir} \
    CLIENTBINDIR=%{buildroot}%{bindir} \
    CLIENTCONFDIR=%{buildroot}%{confdir} \
    CLIENTLIBDIR=%{buildroot}%{libdir} \
    CLIENTVARDIR=%{buildroot}%{vardir} \
    SERVERREXECDIR=%{buildroot}%{rexecdir} \
    COMMONDIR=%{buildroot}%{commondir} \
    COMMONDATADIR=%{buildroot}%{commondir} \
    COMMONSHLIBDIR=%{buildroot}%{commondir} \
    CLIENTMANDIR=%{buildroot}%{_mandir} \
    SERVERMANDIR=%{buildroot}%{_mandir}

make install.rexeclinks \
    CLIENTBINDIR=%{bindir} \
    SERVERREXECDIR=%{buildroot}%{rexecdir}

# fix afbackup verify error
rm -f %{buildroot}%{rexecdir}/verify
ln -s %{bindir}/afverify %{buildroot}%{rexecdir}/verify
echo %{cryptkey} >%{buildroot}%{confdir}/cryptkey

%post
grep -q '/usr/lib/afbackup/rexec' %{confdir}/%{serverconf} && {
echo "Upgrade afserver.conf"
sed 's,/usr/lib/afbackup/rexec,%{rexecdir},' %{confdir}/%{serverconf} >%{confdir}/%{serverconf}.%{version}
cat %{confdir}/%{serverconf}.%{version} >%{confdir}/%{serverconf}
}

if ! grep -q ^afbackup %{_sysconfdir}/services
then
echo "afbackup        2988/tcp                        # Afbackup system" >>%{_sysconfdir}/services
fi

if ! grep -q ^afmbackup %{_sysconfdir}/services
then
echo "afmbackup        2989/tcp                        # Afbackup system Multistream" >>%{_sysconfdir}/services
fi

if [ -f %{_sysconfdir}/inetd.conf ]
then
    if ! grep -q afbackup %{_sysconfdir}/inetd.conf
    then
    echo "afbackup stream tcp     nowait  root    %{bindir}/afserver %{bindir}afserver %{confdir}/%{serverconf}" >>%{_sysconfdir}/inetd.conf
    fi
fi

/sbin/chkconfig --add afbackup

%post client
grep -q '/usr/lib/afbackup/rexec' %{confdir}/%{serverconf} && {
echo "Upgrade afserver.conf"
sed 's,/usr/lib/afbackup/rexec,%{rexecdir},' %{confdir}/%{serverconf} >%{confdir}/%{serverconf}.%{version}
cat %{confdir}/%{serverconf}.%{version} >%{confdir}/%{serverconf}
}


if ! grep -q ^afbackup %{_sysconfdir}/services
then
echo "afbackup        2988/tcp                        # Afbackup system" >>%{_sysconfdir}/services
fi

if ! grep -q ^afmbackup %{_sysconfdir}/services
then
echo "afmbackup        2989/tcp                        # Afbackup system Multistream" >>%{_sysconfdir}/services
fi

%preun
if [ "$1" = "0" ]; then
  /sbin/service afbackup stop || :
  /sbin/chkconfig --del afbackup || :
fi

%postun
if [ $1 -ge 1 ] ; then
  /sbin/service afbackup condrestart 2>&1 > /dev/null || :
fi

%files
%doc CONFIG INTRO README PROGRAMS
%attr(700,root,adm) %dir %{commondir}
# ATM it's the same as commondir so skip
#attr(700,root,adm) %dir %{rexecdir}
%{rexecdir}/afverify
%{rexecdir}/verify
%{rexecdir}/copy_tape
%{rexecdir}/full_backup
%{rexecdir}/incr_backup
%{rexecdir}/update_indexes
%{rexecdir}/afrestore
%dir %{confdir}/init.d
%config(noreplace) %{_sysconfdir}/xinetd.d/afbackup-xinetd
%config(noreplace) %{_sysconfdir}/afbackup/init.d/afbackup
%attr(755,root,root) %config(noreplace) %{_initrddir}/afbackup
%attr(750,root,adm) %dir %{confdir}
%attr(640,root,adm) %config(noreplace) %{confdir}/%{serverconf}
%attr(640,root,adm) %config(noreplace) %{confdir}/changer.conf
%attr(640,root,adm) %config(noreplace) %{confdir}/%{clientconf}
%attr(600,root,adm) %config(noreplace) %{confdir}/cryptkey
%attr(640,root,adm) %{commondir}/aftcllib.tcl
%attr(711,root,adm) %dir %{vardir}
%attr(640,root,adm) %config(noreplace) %{vardir}/readonly_tapes
%attr(750,root,adm) %dir %{logdir}
%attr(750,root,adm) %{bindir}/afbackout
%attr(750,root,adm) %{bindir}/afbackup
%attr(750,root,adm) %{bindir}/afclient
%attr(750,root,adm) %{bindir}/afclientconfig
%attr(750,root,adm) %{bindir}/afmserver
%attr(750,root,adm) %{bindir}/afrestore
%attr(750,root,adm) %{bindir}/afserver
%attr(750,root,adm) %{bindir}/afserverconfig
%attr(750,root,adm) %{bindir}/afverify
%attr(750,root,adm) %{bindir}/autocptapes
%attr(750,root,adm) %{bindir}/cartagehandler
%attr(750,root,adm) %{bindir}/cart_ctl
%attr(750,root,adm) %{bindir}/cartis
%attr(750,root,adm) %{bindir}/cartready
%attr(750,root,adm) %{bindir}/changerready
%attr(750,root,adm) %{bindir}/copy_tape
%attr(750,root,adm) %{bindir}/full_backup
%attr(750,root,adm) %{bindir}/incr_backup
%attr(750,root,adm) %{bindir}/label_tape
%attr(750,root,adm) %{bindir}/serverconfig
%attr(750,root,adm) %{bindir}/update_indexes
%attr(750,root,adm) %{bindir}/xafclientconfig
%attr(750,root,adm) %{bindir}/xafrestore
%attr(750,root,adm) %{bindir}/xafserverconfig
%attr(750,root,adm) %{bindir}/xafserverstatus
%attr(750,root,adm) %{bindir}/xserverconfig
%attr(750,root,adm) %{bindir}/xserverstatus
%attr(750,root,adm) %{bindir}/__descrpt
%attr(750,root,adm) %{bindir}/__inc_link
%attr(750,root,adm) %{bindir}/__mt
%attr(750,root,adm) %{bindir}/__numset
%attr(750,root,adm) %{bindir}/__packpats
%attr(750,root,adm) %{bindir}/__piper
%attr(750,root,adm) %{bindir}/__z
%{_mandir}/*/*

%files client
%doc CONFIG INTRO README PROGRAMS
%attr(750,root,adm) %dir %{commondir}
%attr(750,root,adm) %dir %{confdir}
%attr(711,root,adm) %dir %{vardir}
%attr(750,root,adm) %dir %{logdir}
%attr(750,root,adm) %{bindir}/clientconfig
%attr(750,root,adm) %{bindir}/xclientconfig
%attr(750,root,adm) %{bindir}/xrestore



