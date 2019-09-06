<?php
function exec_sql($sql, $connect) {
	if (!mysqli_query($connect, $sql)) {
		print "Unable to execute SQL statement ($sql): " . mysqli_error($connect) . "\n";
		exit(1);
	}
}

function split_sql($sql, $handler_func, $connect) {
	$in_string = false;
	$in_comment = false;
	$start = 0;
	$len = strlen($sql);

	for ($i = 0; $i < $len; $i++) {
		if (($sql[$i] == "#" || ($sql[$i] == "-" && $sql[$i+1] == "-")) && !$in_string) {
			$in_comment = true;
			continue;
		}

		if ($sql[$i] == "\n" && $in_comment) {
			$in_comment = false;
			$start = $i+1;
			continue;
		}

		if ($in_comment)
			continue;

		if ($sql[$i] == ";" && !$in_string) {
			$statement = substr($sql, $start, $i - $start);
			if (!preg_match("/^[ \n\r\t]*$/", $statement))
				call_user_func($handler_func, $statement, $connect);
			$start = $i+1;
		}

		if ($sql[$i] == $in_string && $sql[$i-1] != "\\") {
			$in_string = false;
		} elseif (($sql[$i] == '"' || $sql[$i] == "'") && !$in_string && ($i > 0 && $sql[$i-1] != "\\")) {
			$in_string = $sql[$i];
		}
	}

	if (!$in_comment) {
		$statement = substr($sql, $start);

		if (!preg_match("/^[ \n\r\t]*$/", $statement))
			call_user_func($handler_func, $statement, $connect);
	}
}

function mysql_db_connect($host, $username, $passwd, $dbname, $port) {
	$connect = mysqli_connect($host, $username, $passwd, '', $port);
	if (!$connect) {
		print "Unable to connect to DB: " . mysqli_connect_error() . "\n";
		exit(1);
	}

	if (!mysqli_select_db($connect, $dbname)) {
		print "Unable to select $dbname database: " . mysqli_error($connect) . "\n";
		exit(1);
	}
	return $connect;
}

function populate_mysql_db($sql, $connect) {
	$sql = split_sql($sql, "exec_sql", $connect);
}
?>