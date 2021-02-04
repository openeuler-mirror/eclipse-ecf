%global _eclipsedir %{_prefix}/lib/eclipse
%global __requires_exclude .*org\.eclipse\.equinox.*
%global git_tag 5d501929b628b6aa6d28b2f5df73fc45c0fa1945
%bcond_with bootstrap
Name:                eclipse-ecf
Version:             3.14.4
Release:             3
Summary:             Eclipse Communication Framework (ECF) Eclipse plug-in
License:             EPL-1.0 and ASL 2.0
URL:                 http://www.eclipse.org/ecf/
Source0:             http://git.eclipse.org/c/ecf/org.eclipse.ecf.git/snapshot/org.eclipse.ecf-%{git_tag}.tar.xz
Patch0:              eclipse-ecf-feature-deps.patch
Patch1:              CVE-2014-0363.patch
BuildRequires:       tycho tycho-extras maven-plugin-build-helper eclipse-license osgi-annotation
BuildRequires:       xpp3-minimal httpcomponents-client httpcomponents-core apache-commons-codec
BuildRequires:       apache-commons-logging
%if %{without bootstrap}
BuildRequires:       eclipse-emf-runtime eclipse-pde
%endif
BuildArch:           noarch
%description
ECF is a set of frameworks for building communications into applications and
services. It provides a lightweight, modular, transport-independent, fully
compliant implementation of the OSGi Remote Services standard.

%package   core
Summary:             Eclipse ECF Core
Requires:            httpcomponents-client httpcomponents-core
%description core
ECF bundles required by eclipse-platform.
%if %{without bootstrap}

%package   runtime
Summary:             Eclipse Communication Framework (ECF) Eclipse plug-in
%description runtime
ECF is a set of frameworks for building communications into applications and
services. It provides a lightweight, modular, transport-independent, fully
compliant implementation of the OSGi Remote Services standard.

%package   sdk
Summary:             Eclipse ECF SDK
%description sdk
Documentation and developer resources for the Eclipse Communication Framework
(ECF) plug-in.
%endif

%prep
%setup -q -n org.eclipse.ecf-%{git_tag}
find . -type f -name "*.jar" -exec rm {} \;
find . -type f -name "*.class" -exec rm {} \;
%patch0
%patch1 -p1
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.presence']" releng/features/org.eclipse.ecf.core/feature.xml
sed -i -e '/org.objectweb.asm/s/7/8/' protocols/bundles/ch.ethz.iks.r_osgi.remote/META-INF/MANIFEST.MF
sed -i -e '/<module>examples/d' -e '/<module>tests/d' pom.xml
%pom_disable_module releng/features/org.eclipse.ecf.tests.feature
%pom_disable_module releng/features/org.eclipse.ecf.eventadmin.examples.feature
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.examples.feature
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.sdk.examples.feature
%pom_xpath_remove "feature/requires/import[@feature='org.eclipse.ecf.remoteservice.sdk.examples.feature']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.example.clients']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.example.collab']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "pom:target"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:dependencies"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:sourceReferences"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:timestampProvider"
%pom_disable_module releng/org.eclipse.ecf.releng.repository
%pom_xpath_remove "feature/requires/import[@plugin='org.json']" releng/features/org.eclipse.ecf.remoteservice.rest.feature/feature.xml
%pom_disable_module releng/features/org.eclipse.ecf.discovery.zookeeper.feature
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.zookeeper
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.discovery.zookeeper.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.rest.synd.feature
%pom_disable_module framework/bundles/org.eclipse.ecf.remoteservice.rest.synd
%pom_disable_module releng/features/org.eclipse.ecf.discovery.slp.feature
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.jslp
%pom_disable_module protocols/bundles/ch.ethz.iks.slp
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.discovery.slp.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml
%pom_disable_module releng/features/org.eclipse.ecf.discovery.dnssd.feature
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.dnssd
%pom_disable_module protocols/bundles/org.jivesoftware.smack
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.datashare
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.remoteservice
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.ui
%pom_disable_module releng/features/org.eclipse.ecf.xmpp.feature
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.xmpp.ui']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.irc
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.irc.ui
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.irc']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.irc.ui']" releng/features/org.eclipse.ecf.core/feature.xml
ln -s $(build-classpath osgi-annotation) osgi/bundles/org.eclipse.osgi.services.remoteserviceadmin/osgi/osgi.annotation.jar
%if %{with bootstrap}
%pom_xpath_replace "pom:modules" "<modules>
<module>releng/features/org.eclipse.ecf.core.feature</module>
<module>releng/features/org.eclipse.ecf.core.ssl.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.httpclient4.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.httpclient4.ssl.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.ssl.feature</module>
<module>framework/bundles/org.eclipse.ecf</module>
<module>framework/bundles/org.eclipse.ecf.identity</module>
<module>framework/bundles/org.eclipse.ecf.filetransfer</module>
<module>framework/bundles/org.eclipse.ecf.ssl</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4.ssl</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.ssl</module>
</modules>"
%endif
sed -i -e '/Require-Bundle:/a\ org.eclipse.osgi.services,' framework/bundles/org.eclipse.ecf.console/META-INF/MANIFEST.MF
%mvn_package "::{pom,target}::" __noinstall
%if %{with bootstrap}
%mvn_package "::jar:{sources,sources-feature}:" __noinstall
%else
%mvn_package "::jar:{sources,sources-feature}:" sdk
%endif
%mvn_package ":org.eclipse.ecf.{core,sdk}" sdk
%mvn_package ":org.eclipse.ecf.docshare*" sdk
for p in $(grep '<plugin' releng/features/org.eclipse.ecf.core/feature.xml | sed -e 's/.*id="\(.*\)" d.*/\1/') ; do
%mvn_package ":$p" sdk
done
%mvn_package ":*.ui" sdk
%mvn_package ":*.ui.*" sdk
%mvn_package ":org.eclipse.ecf.remoteservice.sdk.*" sdk
%mvn_package ":org.eclipse.ecf.core.{,ssl.}feature"
%mvn_package ":org.eclipse.ecf.filetransfer.{,httpclient4.}{,ssl.}feature"
%mvn_package ":org.eclipse.ecf{,.identity,.ssl,.filetransfer}"
%mvn_package ":org.eclipse.ecf.provider.filetransfer*"
%mvn_package ":" runtime

%build
QUALIFIER=$(date -u -d"$(stat --format=%y %{SOURCE0})" +v%Y%m%d-%H%M)
%mvn_build -j -- -DforceContextQualifier=$QUALIFIER

%install
%mvn_install
install -d -m 755 %{buildroot}%{_eclipsedir}
mv %{buildroot}%{_datadir}/eclipse/droplets/ecf/{plugins,features} %{buildroot}%{_eclipsedir}
rm -r %{buildroot}%{_datadir}/eclipse/droplets/ecf
sed -i -e 's|%{_datadir}/eclipse/droplets/ecf|%{_eclipsedir}|' %{buildroot}%{_datadir}/maven-metadata/eclipse-ecf.xml
sed -i -e 's|%{_datadir}/eclipse/droplets/ecf/features/|%{_eclipsedir}/features/|' \
       -e 's|%{_datadir}/eclipse/droplets/ecf/plugins/|%{_eclipsedir}/plugins/|' .mfiles
sed -i -e '/droplets/d' .mfiles
for del in $( (cd %{buildroot}%{_eclipsedir}/plugins && ls | grep -v -e '^org\.eclipse\.ecf' ) ) ; do
rm %{buildroot}%{_eclipsedir}/plugins/$del
sed -i -e "/$del/d" .mfiles
done
install -d -m 755 %{buildroot}%{_javadir}/eclipse
location=%{_eclipsedir}/plugins
while [ "$location" != "/" ] ; do
    location=$(dirname $location)
    updir="$updir../"
done
pushd %{buildroot}%{_javadir}/eclipse
for J in ecf{,.identity,.ssl,.filetransfer,.provider.filetransfer{,.ssl,.httpclient4{,.ssl}}}  ; do
    DIR=$updir%{_eclipsedir}/plugins
    [ -e "`ls $DIR/org.eclipse.${J}_*.jar`" ] && ln -s $DIR/org.eclipse.${J}_*.jar ${J}.jar
done
popd

%files core -f .mfiles
%{_javadir}/eclipse/*
%if %{without bootstrap}

%files runtime -f .mfiles-runtime

%files sdk -f .mfiles-sdk
%endif

%changelog
* Thu Feb 4 2021 wutao <wutao61@huawei.com> - 3.14.4-3
- remove irclib deps

* Sat Dec 12 2020 caodongxia <caodongxia@huawei.com> - 3.14.4-2
- Fix CVE-2014-0363.patch

* Thu Aug 27 2020 yanan li <liyanan032@huawei.com> - 3.14.4-1
- Package init
