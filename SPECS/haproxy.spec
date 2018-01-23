%define haproxy_user    haproxy
%define haproxy_uid     188
%define haproxy_group   haproxy
%define haproxy_gid     188
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy

%define version 1.8.3

Name: haproxy
Summary: HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Version: %{version}
Release: 1
License: GPL
URL: http://www.haproxy.org/
Group: System Environment/Daemons

Source0: http://www.haproxy.org/download/1.8/src/%{name}-%{version}.tar.gz
Source1: %{name}.init
Source2: %{name}.cfg
Source3: %{name}.logrotate

BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)

BuildRequires: pcre-devel openssl-devel zlib-devel
BuildRequires: setup >= 2.5

Requires(pre): %{_sbindir}/groupadd
Requires(pre): %{_sbindir}/useradd
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

Requires: pcre openssl zlib

%description
HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q -n %{name}-%{version}

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
%{__make} USE_OPENSSL=yes USE_PCRE=1 USE_LUA=yes LUA_LIB=/usr/local/lib/ LUA_INC=/usr/local/include/ USE_ZLIB=1 DEBUG="" ARCH=%{_target_cpu} TARGET=linux26

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

make install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix}
make install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
#%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}

for file in $(find . -type f -name '*.txt') ; do
    iconv -f ISO-8859-1 -t UTF-8 -o $file.new $file && \
    touch -r $file $file.new && \
    mv $file.new $file
done

find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%pre
%{_sbindir}/groupadd -g %{haproxy_gid} -r %{haproxy_group} 2>/dev/null || :
%{_sbindir}/useradd -u %{haproxy_uid} -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -r %{haproxy_user} 2>/dev/null || :

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc CHANGELOG LICENSE README doc/*
%{haproxy_datadir}
%dir %{haproxy_confdir}
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
#%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_initrddir}/%{name}
%{_sbindir}/%{name}
%{_mandir}/man1/%{name}.1.gz
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}

%changelog
* Sun Dec 27 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6.3

* Tue Nov  3 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6.2

* Tue Oct 20 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6.1

* Tue Oct 13 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6.0

* Tue Oct  6 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev7

* Mon Sep 28 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev6

* Mon Sep 14 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev5

* Sun Aug 30 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev4

* Sun Aug 30 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev4

* Wed Jul 22 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev3

* Wed Jun 17 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev2

* Wed Mar 11 2015 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev1

* Thu Jun 19 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.6-dev0

* Thu Jun 19 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5.0

* Wed May 28 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev26

* Sat May 10 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev25

* Sat Apr 26 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev24

* Wed Apr 23 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev23

* Mon Feb  3 2014 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev22

* Tue Dec 17 2013 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev21

* Mon Dec 16 2013 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev20

* Mon Jun 17 2013 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev19

* Wed Apr  3 2013 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev18

* Fri Dec 28 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev17

* Mon Dec 24 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev16

* Wed Dec 12 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev15

* Mon Nov 26 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev14

* Thu Nov 22 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev13

* Mon Sep 10 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev12

* Mon Jun  4 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev11

* Mon May 14 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev10

* Tue May  8 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev9

* Mon Mar 26 2012 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev8

* Sat Sep 10 2011 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev7

* Fri Apr  8 2011 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev6

* Tue Mar 29 2011 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev5

* Sun Mar 13 2011 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev4

* Thu Nov 11 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev3

* Sat Aug 28 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev2

* Wed Aug 25 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev1

* Sun May 23 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.5-dev0

* Sun May 16 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.6

* Thu May 13 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.5

* Wed Apr  7 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.4

* Tue Mar 30 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.3

* Wed Mar 17 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.2

* Thu Mar  4 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.1

* Fri Feb 26 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4.0

* Tue Feb  2 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4-rc1

* Mon Jan 25 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev8

* Mon Jan 25 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev7

* Fri Jan  8 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev6

* Sun Jan  3 2010 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev5

* Mon Oct 12 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev4

* Thu Sep 24 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev3

* Sun Aug  9 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev2

* Wed Jul 29 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev1

* Tue Jun 09 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.4-dev0

* Sun May 10 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.3.18

* Sun Mar 29 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.3.17

* Sun Mar 22 2009 Willy Tarreau <w@1wt.eu>
- updated to 1.3.16

* Sat Apr 19 2008 Willy Tarreau <w@1wt.eu>
- updated to 1.3.15

* Wed Dec  5 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.14

* Thu Oct 18 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.13

* Sun Jun 17 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.12

* Sun Jun  3 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.11.4

* Mon May 14 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.11.3

* Mon May 14 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.11.2

* Mon May 14 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.11.1

* Mon May 14 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.11

* Thu May 10 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.10.2

* Tue May 09 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.10.1

* Tue May 08 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.10

* Sun Apr 15 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.9

* Tue Apr 03 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.8.2

* Sun Apr 01 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.8.1

* Sun Mar 25 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.8

* Wed Jan 26 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.7

* Wed Jan 22 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.6

* Wed Jan 07 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.5

* Wed Jan 02 2007 Willy Tarreau <w@1wt.eu>
- updated to 1.3.4

* Wed Oct 15 2006 Willy Tarreau <w@1wt.eu>
- updated to 1.3.3

* Wed Sep 03 2006 Willy Tarreau <w@1wt.eu>
- updated to 1.3.2

* Wed Jul 09 2006 Willy Tarreau <w@1wt.eu>
- updated to 1.3.1

* Wed May 21 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.14

* Wed May 01 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.13

* Wed Apr 15 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.12

* Wed Mar 30 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.11.1

* Wed Mar 19 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.10

* Wed Mar 15 2006 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.9

* Sat Jan 22 2005 Willy Tarreau <willy@w.ods.org>
- updated to 1.2.3 (1.1.30)

* Sun Nov 14 2004 Willy Tarreau <w@w.ods.org>
- updated to 1.1.29
- fixed path to config and init files
- statically linked PCRE to increase portability to non-pcre systems

* Sun Jun  6 2004 Willy Tarreau <willy@w.ods.org>
- updated to 1.1.28
- added config check support to the init script

* Tue Oct 28 2003 Simon Matter <simon.matter@invoca.ch>
- updated to 1.1.27
- added pid support to the init script

* Wed Oct 22 2003 Simon Matter <simon.matter@invoca.ch>
- updated to 1.1.26

* Thu Oct 16 2003 Simon Matter <simon.matter@invoca.ch>
- initial build
