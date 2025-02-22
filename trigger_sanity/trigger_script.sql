WITH RECURSIVE fkeys AS (

	  /* source and target tables for all foreign keys */
	  SELECT 
		connamespace :: regnamespace :: text as schema_name, 
		conrelid AS source, 
		confrelid AS target 
	  FROM 
		pg_constraint 
	  WHERE 
		contype = 'f' 
		and conrelid <> confrelid
		and connamespace :: regnamespace :: text LIKE ANY (ARRAY [ '<<postgres_schema_name>>' ])
	), 
	tables AS (
	  (

		/* all tables ... */
		SELECT 
		  relnamespace :: regnamespace :: text as schema_name, 
		  oid AS table_name, 
		  1 AS level, 
		  ARRAY [oid] AS trail, 
		  FALSE AS circular 
		FROM 
		  pg_class 
		WHERE 
		  relkind = 'r' 
		  AND relnamespace::regnamespace ::text LIKE ANY (ARRAY [ '<<postgres_schema_name>>' ]) 
		EXCEPT 

		  /* ... except the ones that have a foreign key */
		SELECT 
		  schema_name, 
		  source, 
		  1, 
		  ARRAY [ source ], 
		  FALSE 
		FROM 
		  fkeys
	  ) 
	  UNION ALL 

		/* all tables with a foreign key pointing a table in the working set */
	  SELECT 
		tables.schema_name, 
		fkeys.source, 
		tables.level + 1, 
		tables.trail || fkeys.source, 
		tables.trail @> ARRAY [fkeys.source] 
	  FROM 
		fkeys 
		JOIN tables ON tables.table_name = fkeys.target 
		/*        * Stop when a table appears in the trail the third time.        * This way, we get the table once with "circular = TRUE".        */
	  WHERE 
		cardinality(
		  array_positions(tables.trail, fkeys.source)
		) < 2
	), 
	ordered_tables AS (

	  /* get the highest level per table */
	  SELECT 
		DISTINCT ON (schema_name, table_name) schema_name, 
		table_name, 
		level, 
		circular, 
		trail 
	  FROM 
		tables 
	 where not circular
	  ORDER BY 
		schema_name, 
		table_name, 
		level DESC
	), 
	fkorder as (
	  select distinct 
		ordered_tables.schema_name, 
		coalesce(nullif(split_part(ordered_tables.table_name :: regclass :: text, '.', 2),''),ordered_tables.table_name :: regclass :: text) as table_name, 
		pg_class.relname, 
		ordinality as index 
	  from 
		ordered_tables, 
		json_array_elements_text(
		  array_to_json(trail :: text[])
		) with ordinality 
		join pg_class on relkind = 'r' 
		and value :: oid = pg_class.oid
	), 
	ALIAS1 AS (
	  select 
		event_object_schema as table_schema, 
		event_object_table as table_name, 
		trigger_schema, 
		trigger_name, 
		string_agg(event_manipulation, ',') as event_manipulation, 
		action_timing as activation, 
		action_condition as condition, 
		action_statement as definition, 
		fkorder.relname, 
		fkorder.index 
	  from 
		information_schema.triggers, 
		fkorder 
	  where 
		event_object_schema = '<<postgres_schema_name>>' --Change <<postgres_schema_name>>
		and event_object_schema = fkorder.schema_name 
		and event_object_table = coalesce(nullif(fkorder.table_name,''), fkorder.relname)
	  group by 
		1, 
		2, 
		3, 
		4, 
		6, 
		7, 
		8, 
		9, 
		10 
	  order by 
		table_schema, 
		table_name, 
		fkorder.index
	), 
	trigstmt as (
	  select 
		ALIAS1.*, 
		(
		  SELECT 
			'INSERT INTO ' || parameters.table_schema || '.' || parameters.table_name || '(' || STRING_AGG(
			  parameters.column_name, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ') VALUES (' || STRING_AGG(
			  CASE WHEN parameters.data_type IN ('smallint', 'smallserial') THEN '9999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'integer', 'bigint', 'serial', 'bigserial'
			  ) THEN '999999999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'decimal', 'numeric', 'real', 'double precision'
			  ) THEN '987.654' || '::' || parameters.data_type WHEN parameters.data_type IN ('money') THEN '99.07' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'character', 'character varying', 
				'varchar', 'char', 'text'
			  ) THEN '''' || 1 || '''' || '::' || parameters.data_type WHEN parameters.data_type IN ('bytea') THEN 'E' || '''' || '\\\\000' || '''' || '::bytea' WHEN parameters.data_type IN (
				'date', 'time with time zone', 'time without time zone', 
				'timestamp with time zone', 'timestamp without time zone'
			  ) THEN '''' || 'now' || '''' || '::' || parameters.data_type WHEN parameters.data_type in ('boolean') THEN 'true::boolean' WHEN parameters.data_type in ('UUID') THEN 'uuid_generate_v4 ()' ELSE ' ' END, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ');' 
		  FROM 
			information_schema.columns as parameters 
		  WHERE 
			parameters.table_schema = ALIAS1.table_schema 
			AND parameters.table_name = ALIAS1.relname 
			and is_identity = 'NO' 
			and is_generated = 'NEVER' 
			and is_updatable = 'YES' 
			and column_default is null 
		  GROUP BY 
			parameters.table_schema, 
			parameters.table_name 
		  LIMIT 
			1
		) as ins, 
		CASE WHEN relname = table_name then (
		  select 
			'UPDATE ' || parameters.table_schema || '.' || parameters.table_name || ' SET (' || STRING_AGG(
			  parameters.column_name, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ') = (SELECT  ' || STRING_AGG(
			  CASE WHEN parameters.data_type IN ('smallint', 'smallserial') THEN '9999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'integer', 'bigint', 'serial', 'bigserial'
			  ) THEN '999999999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'decimal', 'numeric', 'real', 'double precision'
			  ) THEN '987.654' || '::' || parameters.data_type WHEN parameters.data_type IN ('money') THEN '99.07' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'character', 'character varying', 
				'varchar', 'char', 'text'
			  ) THEN '''' || 1 || '''' || '::' || parameters.data_type WHEN parameters.data_type IN ('bytea') THEN 'E' || '''' || '\\\\000' || '''' || '::bytea' WHEN parameters.data_type IN (
				'date', 'time with time zone', 'time without time zone', 
				'timestamp with time zone', 'timestamp without time zone'
			  ) THEN '''' || 'now' || '''' || '::' || parameters.data_type WHEN parameters.data_type in ('boolean') THEN 'true::boolean' WHEN parameters.data_type in ('UUID') THEN 'uuid_generate_v4 ()' ELSE ' ' END, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ') WHERE ' || '(' || STRING_AGG(
			  parameters.column_name, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ')' || ' = ' || '( SELECT  ' || STRING_AGG(
			  CASE WHEN parameters.data_type IN ('smallint', 'smallserial') THEN '9999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'integer', 'bigint', 'serial', 'bigserial'
			  ) THEN '999999999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'decimal', 'numeric', 'real', 'double precision'
			  ) THEN '987.654' || '::' || parameters.data_type WHEN parameters.data_type IN ('money') THEN '99.07' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'character', 'character varying', 
				'varchar', 'char', 'text'
			  ) THEN '''' || 1 || '''' || '::' || parameters.data_type WHEN parameters.data_type IN ('bytea') THEN 'E' || '''' || '\\\\000' || '''' || '::bytea' WHEN parameters.data_type IN (
				'date', 'time with time zone', 'time without time zone', 
				'timestamp with time zone', 'timestamp without time zone'
			  ) THEN '''' || 'now' || '''' || '::' || parameters.data_type WHEN parameters.data_type in ('boolean') THEN 'true::boolean' WHEN parameters.data_type in ('UUID') THEN 'uuid_generate_v4 ()' ELSE ' ' END, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ');' 
		  FROM 
			information_schema.columns as parameters 
		  WHERE 
			parameters.table_schema = ALIAS1.table_schema 
			AND parameters.table_name = ALIAS1.relname 
			and is_identity = 'NO' 
			and is_generated = 'NEVER' 
			and is_updatable = 'YES' 
			and column_default is null --and is_nullable = 'NO'
		  GROUP BY 
			parameters.table_schema, 
			parameters.table_name 
		  LIMIT 
			1
		) else null end as upd, 
		CASE WHEN relname = table_name then (
		  select 
			'DELETE FROM ' || parameters.table_schema || '.' || parameters.table_name || ' WHERE ' || '(' || STRING_AGG(
			  parameters.column_name, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ')' || ' = ' || '( SELECT  ' || STRING_AGG(
			  CASE WHEN parameters.data_type IN ('smallint', 'smallserial') THEN '9999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'integer', 'bigint', 'serial', 'bigserial'
			  ) THEN '999999999' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'decimal', 'numeric', 'real', 'double precision'
			  ) THEN '987.654' || '::' || parameters.data_type WHEN parameters.data_type IN ('money') THEN '99.07' || '::' || parameters.data_type WHEN parameters.data_type IN (
				'character', 'character varying', 
				'varchar', 'char', 'text'
			  ) THEN '''' || 1 || '''' || '::' || parameters.data_type WHEN parameters.data_type IN ('bytea') THEN 'E' || '''' || '\\000' || '''' || '::bytea' WHEN parameters.data_type IN (
				'date', 'time with time zone', 'time without time zone', 
				'timestamp with time zone', 'timestamp without time zone'
			  ) THEN '''' || 'now' || '''' || '::' || parameters.data_type WHEN parameters.data_type in ('boolean') THEN 'true::boolean' WHEN parameters.data_type in ('UUID') THEN 'uuid_generate_v4 ()' ELSE ' ' END, 
			  ',' 
			  ORDER BY 
				parameters.ordinal_position
			) || ');' 
		  FROM 
			information_schema.columns as parameters 
		  WHERE 
			parameters.table_schema = ALIAS1.table_schema 
			AND parameters.table_name = ALIAS1.relname 
			and is_identity = 'NO' 
			and is_generated = 'NEVER' 
			and is_updatable = 'YES' 
			and column_default is null --and is_nullable = 'NO'
		  GROUP BY 
			parameters.table_schema, 
			parameters.table_name 
		  LIMIT 
			1
		) else null end as del 
	  from 
		ALIAS1 
	  order by 
		trigger_schema, 
		trigger_name, 
		index
	), 
	trigstmtagg as (
	  select 
		table_schema, 
		table_name, 
		trigger_schema, 
		trigger_name, 
		event_manipulation, 
		activation, 
		STRING_AGG(
		  ins, 
		  E'\n' 
		  order by 
			index
		) ins_agg, 
		STRING_AGG(
		  upd, 
		  E'\n' 
		  order by 
			index
		) upd_agg, 
		STRING_AGG(
		  del, 
		  E'\n' 
		  order by 
			index
		) del_agg 
	  from 
		trigstmt 
	  group by 
		table_schema, 
		table_name, 
		trigger_schema, 
		trigger_name, 
		event_manipulation, 
		activation
	) 
	select 
	  table_schema, 
	  table_name, 
	  trigger_schema, 
	  trigger_name, 
	  event_manipulation, 
	  activation, 
	  'BEGIN; ' || E'\n' || case when event_manipulation like '%INSERT%' 
	  AND event_manipulation NOT like '%DELETE%' 
	  AND event_manipulation NOT like '%UPDATE%' THEN ins_agg WHEN event_manipulation like '%UPDATE%' 
	  AND event_manipulation NOT like '%DELETE%' 
	  AND event_manipulation NOT like '%INSERT%' THEN ins_agg || E'\n' || upd_agg WHEN event_manipulation like '%DELETE%' 
	  AND event_manipulation NOT like '%UPDATE%' 
	  AND event_manipulation NOT like '%INSERT%' THEN ins_agg || E'\n' || del_agg else ins_agg || E'\n' || upd_agg || E'\n' || del_agg end || E'\n' || 'ROLLBACK;' as final_statement 
	from 
	  trigstmtagg


