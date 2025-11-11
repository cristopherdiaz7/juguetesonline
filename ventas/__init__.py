try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# PyMySQL not installed in the environment; if mysqlclient is available
	# we'll use it instead. This keeps containers working when PyMySQL isn't
	# provided but mysqlclient (native) is present.
	pass
