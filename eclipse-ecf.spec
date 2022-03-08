%global _eclipsedir %{_prefix}/lib/eclipse
%global __requires_exclude .*org\.eclipse\.equinox.*
%global git_tag bc2e29e0d5cf49d05bd97dbb082d2ab58eedd13b 
%bcond_with bootstrap
Name:                eclipse-ecf
Version:             3.14.19
Release:             2
Summary:             Eclipse Communication Framework (ECF) Eclipse plug-in
License:             EPL-1.0 and ASL 2.0
URL:                 http://www.eclipse.org/ecf/
Source0:             http://git.eclipse.org/c/ecf/org.eclipse.ecf.git/snapshot/org.eclipse.ecf-%{git_tag}.tar.xz
Patch0:              0001-Avoid-hard-coding-dependency-versions-by-using-featu.patch
Patch1:              CVE-2014-0363.patch
Patch2:              0002-Remove-unneeded-dep-on-jdt-annotations.patch
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
Requires:  httpcomponents-client
Requires:  httpcomponents-core
# Obsolete SDK and runtime packages since F33
Obsoletes: %{name}-runtime < 3.14.17-3
Obsoletes: %{name}-sdk < 3.14.17-3

%prep
%setup -q -n org.eclipse.ecf-%{git_tag}
find . -type f -name "*.jar" -exec rm {} \;
find . -type f -name "*.class" -exec rm {} \;
%patch0 -p1
%patch1 -p1
%patch2 -p1

# Requires Optional from Java 8
sed -i -e 's/JavaSE-1.7/JavaSE-1.8/' providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient45/META-INF/MANIFEST.MF

# Don't use target platform or jgit packaging bits
%pom_xpath_remove "pom:target"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:dependencies"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:sourceReferences"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:timestampProvider"
%pom_disable_module releng/org.eclipse.ecf.releng.repository

# Don't build bundles that are not relevant to our platform
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient45.win32
%pom_xpath_remove "feature/plugin[@os='win32']" releng/features/org.eclipse.ecf.filetransfer.httpclient45.feature/feature.xml

# Only build core modules needed by Eclipse platform
%pom_xpath_replace "pom:modules" "<modules>
<module>releng/features/org.eclipse.ecf.core.feature</module>
<module>releng/features/org.eclipse.ecf.core.ssl.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.httpclient4.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.httpclient4.ssl.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.httpclient45.feature</module>
<module>releng/features/org.eclipse.ecf.filetransfer.ssl.feature</module>
<module>framework/bundles/org.eclipse.ecf</module>
<module>framework/bundles/org.eclipse.ecf.identity</module>
<module>framework/bundles/org.eclipse.ecf.filetransfer</module>
<module>framework/bundles/org.eclipse.ecf.ssl</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4.ssl</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient45</module>
<module>providers/bundles/org.eclipse.ecf.provider.filetransfer.ssl</module>
</modules>"

%mvn_package "::{pom,target}::" __noinstall

%mvn_package "::jar:{sources,sources-feature}:" __noinstall
%mvn_package ":"

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

%changelog
* Mon Mar 07 2022 xu_ping <tc@openeuler.org> - 3.14.19-2
- add filetransfer.httpclient4 and filetransfer.httpclient4.ssl for tycho

* Tue Jan 18 2022 SimpleUpdate Robot <tc@openeuler.org> - 3.14.19-1
- Upgrade to version 3.14.19

* Thu Feb 4 2021 wutao <wutao61@huawei.com> - 3.14.4-3
- remove irclib deps

* Sat Dec 12 2020 caodongxia <caodongxia@huawei.com> - 3.14.4-2
- Fix CVE-2014-0363.patch

* Thu Aug 27 2020 yanan li <liyanan032@huawei.com> - 3.14.4-1
- Package init
