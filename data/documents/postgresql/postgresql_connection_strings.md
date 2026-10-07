# PostgreSQL Connection Strings and Environment Variables

Source: PostgreSQL Documentation
URL: https://www.postgresql.org/docs/18/libpq-connect.html
Version: 18
License: PostgreSQL (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Connection Strings

Several libpq functions parse a user-specified string to obtain connection parameters. There are two accepted formats for these strings: plain keyword/value strings and URIs. URIs generally follow [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986), except that multi-host connection strings are allowed as further described below.

### Keyword/Value Connection Strings

In the keyword/value format, each parameter setting is in the form <keyword> `=` <value>, with space(s) between settings. Spaces around a setting's equal sign are optional. To write an empty value, or a value containing spaces, surround it with single quotes, for example `keyword = 'a value'`. Single quotes and backslashes within a value must be escaped with a backslash, i.e., `\'` and `\\`.

Example:

    host=localhost port=5432 dbname=mydb connect_timeout=10

The recognized parameter key words are listed in Parameter Key Words.

### Connection URIs

The general form for a connection URI is: postgresql://[<userspec>@][<hostspec>][/<dbname>][?<paramspec>] where <userspec> is: <user>[:<password>] and <hostspec> is: [<host>][:<port>][,...] and <paramspec> is: <name>=<value>[&...]

The URI scheme designator can be either `postgresql://` or `postgres://`. Each of the remaining URI parts is optional. The following examples illustrate valid URI syntax:

    postgresql://
    postgresql://localhost
    postgresql://localhost:5433
    postgresql://localhost/mydb
    postgresql://user@localhost
    postgresql://user:secret@localhost
    postgresql://other@localhost/otherdb?connect_timeout=10&application_name=myapp
    postgresql://host1:123,host2:456/somedb?target_session_attrs=any&application_name=myapp

Values that would normally appear in the hierarchical part of the URI can alternatively be given as named parameters. For example:

    postgresql:///mydb?host=localhost&port=5433

All named parameters must match key words listed in Parameter Key Words, except that for compatibility with JDBC connection URIs, instances of `ssl=true` are translated into `sslmode=require`.

The connection URI needs to be encoded with [percent-encoding](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1) if it includes symbols with special meaning in any of its parts. Here is an example where the equal sign (`=`) is replaced with `%3D` and the space character with `%20`:

    postgresql://user@localhost:5433/mydb?options=-c%20synchronous_commit%3Doff

The host part may be either a host name or an IP address. To specify an IPv6 address, enclose it in square brackets: postgresql://[2001:db8::1234]/database

The host part is interpreted as described for the parameter host. In particular, a Unix-domain socket connection is chosen if the host part is either empty or looks like an absolute path name, otherwise a TCP/IP connection is initiated. Note, however, that the slash is a reserved character in the hierarchical part of the URI. So, to specify a non-standard Unix-domain socket directory, either omit the host part of the URI and specify the host as a named parameter, or percent-encode the path in the host part of the URI:

    postgresql:///dbname?host=/var/lib/postgresql
    postgresql://%2Fvar%2Flib%2Fpostgresql/dbname

It is possible to specify multiple host components, each with an optional port component, in a single URI. A URI of the form `postgresql://host1:port1,host2:port2,host3:port3/` is equivalent to a connection string of the form `host=host1,host2,host3 port=port1,port2,port3`. As further described below, each host will be tried in turn until a connection is successfully established.

### Specifying Multiple Hosts

It is possible to specify multiple hosts to connect to, so that they are tried in the given order. In the Keyword/Value format, the `host`, `hostaddr`, and `port` options accept comma-separated lists of values. The same number of elements must be given in each option that is specified, such that e.g., the first `hostaddr` corresponds to the first host name, the second `hostaddr` corresponds to the second host name, and so forth. As an exception, if only one `port` is specified, it applies to all the hosts.

In the connection URI format, you can list multiple `host:port` pairs separated by commas in the `host` component of the URI.

In either format, a single host name can translate to multiple network addresses. A common example of this is a host that has both an IPv4 and an IPv6 address.

When multiple hosts are specified, or when a single host name is translated to multiple addresses, all the hosts and addresses will be tried in order, until one succeeds. If none of the hosts can be reached, the connection fails. If a connection is established successfully, but authentication fails, the remaining hosts in the list are not tried.

## Selected Connection Parameter Key Words

`host`
Name of host to connect to. If a host name looks like an absolute path name, it specifies Unix-domain communication rather than TCP/IP communication; the value is the name of the directory in which the socket file is stored. (On Unix, an absolute path name begins with a slash. On Windows, paths starting with drive letters are also recognized.) If the host name starts with `@`, it is taken as a Unix-domain socket in the abstract namespace (currently supported on Linux and Windows). The default behavior when `host` is not specified, or is empty, is to connect to a Unix-domain socket in `/tmp` (or whatever socket directory was specified when PostgreSQL was built). On Windows, the default is to connect to `localhost`.

`hostaddr`
Numeric IP address of host to connect to. This should be in the standard IPv4 address format, e.g., `172.28.40.9`. If your machine supports IPv6, you can also use those addresses. TCP/IP communication is always used when a nonempty string is specified for this parameter. If this parameter is not specified, the value of `host` will be looked up to find the corresponding IP address — or, if `host` specifies an IP address, that value will be used directly.

`port`
Port number to connect to at the server host, or socket file name extension for Unix-domain connections. If multiple hosts were given in the `host` or `hostaddr` parameters, this parameter may specify a comma-separated list of ports of the same length as the host list, or it may specify a single port number to be used for all hosts. An empty string, or an empty item in a comma-separated list, specifies the default port number established when PostgreSQL was built.

`dbname`
The database name. Defaults to be the same as the user name. In certain contexts, the value is checked for extended formats; see Connection Strings for more details on those.

`user`
PostgreSQL user name to connect as. Defaults to be the same as the operating system name of the user running the application.

`password`
Password to be used if the server demands password authentication.

`connect_timeout`
Maximum time to wait while connecting, in seconds (write as a decimal integer, e.g., `10`). Zero, negative, or not specified means wait indefinitely. This timeout applies separately to each host name or IP address. For example, if you specify two hosts and `connect_timeout` is 5, each host will time out if no connection is made within 5 seconds, so the total time spent waiting for a connection might be up to 10 seconds.

`application_name`
Specifies a value for the application_name configuration parameter.

`sslmode`
This option determines whether or with what priority a secure SSL TCP/IP connection will be negotiated with the server. There are six modes:

## Environment Variables

The following environment variables can be used to select default connection parameter values, which will be used by PQconnectdb(), PQsetdbLogin() and PQsetdb() if no value is directly specified by the calling code. These are useful to avoid hard-coding database connection information into simple client applications, for example.

- `PGHOST` behaves the same as the host connection parameter.

- `PGSSLNEGOTIATION` behaves the same as the sslnegotiation connection parameter.

- `PGHOSTADDR` behaves the same as the hostaddr connection parameter. This can be set instead of or in addition to `PGHOST` to avoid DNS lookup overhead.

- `PGPORT` behaves the same as the port connection parameter.

- `PGDATABASE` behaves the same as the dbname connection parameter.

- `PGUSER` behaves the same as the user connection parameter.

- `PGPASSWORD` behaves the same as the password connection parameter. Use of this environment variable is not recommended for security reasons, as some operating systems allow non-root users to see process environment variables via ps; instead consider using a password file (see The Password File).

- `PGPASSFILE` behaves the same as the passfile connection parameter.

- `PGREQUIREAUTH` behaves the same as the require_auth connection parameter.

- `PGCHANNELBINDING` behaves the same as the channel_binding connection parameter.

- `PGSERVICE` behaves the same as the service connection parameter.

- `PGSERVICEFILE` specifies the name of the per-user connection service file (see The Connection Service File). Defaults to `~/.pg_service.conf`, or `%APPDATA%\postgresql\.pg_service.conf` on Microsoft Windows.

- `PGOPTIONS` behaves the same as the options connection parameter.

- `PGAPPNAME` behaves the same as the application_name connection parameter.

- `PGSSLMODE` behaves the same as the sslmode connection parameter.

- `PGREQUIRESSL` behaves the same as the requiressl connection parameter. This environment variable is deprecated in favor of the `PGSSLMODE` variable; setting both variables suppresses the effect of this one.

- `PGSSLCOMPRESSION` behaves the same as the sslcompression connection parameter.

- `PGSSLCERT` behaves the same as the sslcert connection parameter.

- `PGSSLKEY` behaves the same as the sslkey connection parameter.

- `PGSSLCERTMODE` behaves the same as the sslcertmode connection parameter.
