<?php
require_once('app-util.php');
require_once('file-util.php');

function upgrade_app($from_ver, $from_rel, $config_files, $db_ids, $psa_modify_hash, $db_modify_hash, $settings_modify_hash, $crypt_settings_modify_hash, $settings_enum_modify_hash, $additional_modify_hash){
    $upgrade_schema_files = array();
    configure($config_files, $upgrade_schema_files, $db_ids, $psa_modify_hash, $db_modify_hash, $settings_modify_hash, $crypt_settings_modify_hash, $settings_enum_modify_hash, $additional_modify_hash);

    $db_id = $db_ids[0];
    $connect = mysql_db_connect(
		get_db_host($db_id),
	    get_db_login($db_id),
	    get_db_password($db_id),
	    get_db_name($db_id),
		get_db_port($db_id)
	);
	$result = mysqli_query($connect, 'SHOW TABLES FROM `' . get_db_name($db_id) . '`');
    if (!$result) {
		print "DB Error, could not list tables\n";
		print 'MySQL Error: ' . mysqli_error($connect);
		exit(1);
    }
	$db_prefix = get_db_prefix($db_id);
    $wp_old_tables = array (
		$db_prefix . 'comments',
		$db_prefix . 'links',
		$db_prefix . 'options',
		$db_prefix . 'postmeta',
		$db_prefix . 'posts',
		$db_prefix . 'terms',
		$db_prefix . 'term_relationships',
		$db_prefix . 'term_taxonomy',
		$db_prefix . 'usermeta',
		$db_prefix . 'users',
    );
    while ($row = mysqli_fetch_row($result)) {
		if (is_array($wp_old_tables) && in_array($row[0], $wp_old_tables )) {
		    switch ($row[0]) {
				case $db_prefix . 'options':
					mysqli_query($connect, "UPDATE " . $row[0] . " SET option_name='" . $db_prefix . "user_roles' WHERE option_name='wp_user_roles';");
					break;
				case $db_prefix . 'usermeta':
					mysqli_query($connect, "UPDATE " . $row[0] . " SET meta_key='" . $db_prefix . "capabilities' WHERE meta_key='wp_capabilities';");
					mysqli_query($connect, "UPDATE " . $row[0] . " SET meta_key='" . $db_prefix . "user_level' WHERE meta_key='wp_user_level';");
					break;
		    }
			mysqli_query($connect, "ALTER TABLE " . $row[0] . " RENAME " . $db_prefix . substr($row['0'], strlen($db_prefix), strlen($row['0']) ) . ";");
		}
    }
    return 0;
}
?>