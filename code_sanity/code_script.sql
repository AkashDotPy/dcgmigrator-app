/*
Mock Callable as per Migrated objects for all procedural blocks
*/
SELECT routines.routine_name , 
          routines.routine_type , 
          routines.specific_schema ,
          'DO $$ '  || e'\n'
            || 
            COALESCE((SELECT 'DECLARE ' ||  e'\n' || string_agg(outparams.parameter_name || ' ' || outparams.data_type  || ';',  '' order by  outparams.ordinal_position)
            FROM information_schema.parameters outparams
            WHERE outparams.parameter_mode IN ('OUT','INOUT')
            AND outparams.specific_schema = routines.specific_schema
            AND outparams.specific_name = routines.specific_name
            ),' ')
            || 'BEGIN' 
             || e'\n' ||
          CASE 
                    WHEN routines.routine_type = 'PROCEDURE' THEN  e'\n' || 'CALL ' 
                    WHEN routines.routine_type = 'FUNCTION' THEN  e'\n' ||  'PERFORM ' 
          END 
                    || routines.specific_schema 
                    || '.' 
                    || routines.routine_name 
                    || '(' 
                    || string_agg( 
          CASE 
                    WHEN parameters.data_type IN ('smallint' , 
                                                  'integer' , 
                                                  'bigint' , 
                                                  'decimal' , 
                                                  'numeric' , 
                                                  'real' , 
                                                  'double precision' , 
                                                  'smallserial' , 
                                                  'serial' , 
                                                  'bigserial'
                                                 ) THEN '1' 
                                        || '::' 
                                        || parameters.data_type 
                    WHEN parameters.data_type IN ( 'decimal' , 
                                                  'numeric' , 
                                                  'real' , 
                                                  'double precision' 
                                                  ) THEN '99.99' 
                                        || '::' 
                                        || parameters.data_type 
                    WHEN parameters.data_type IN ('money') THEN '99.07' 
                                        || '::' 
                                        || parameters.data_type 
                    WHEN parameters.data_type IN ('character' , 
                                                  'character varying' , 
                                                  'varchar' , 
                                                  'char' , 
                                                  'text') THEN '''' 
                                        || 1 
                                        || '''' 
                                        || '::' 
                                        || parameters.data_type 
                    WHEN parameters.data_type IN ('bytea') THEN 'E' 
                                        || '''' 
                                        || '\\000' 
                                        || '''' 
                                        || '::bytea' 
                    WHEN parameters.data_type IN ('date' , 
                                                  'time with time zone' , 
                                                  'time without time zone' , 
                                                  'timestamp with time zone', 
                                                  'timestamp without time zone') THEN '''' 
                                        || 'now' 
                                        || '''' 
                                        || '::' 
                                        || parameters.data_type 
                  WHEN parameters.data_type IN ('boolean') THEN 'true::boolean' 
                  WHEN parameters.data_type IN ('UUID') THEN 'gen_random_uuid()' --Supported in newer version of PG
		      WHEN parameters.data_type IN ('USER-DEFINED')  -- Support one level of values.
			      THEN (select 'ROW(' || STRING_AGG( CASE WHEN att1.data_type IN ( 'smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision', 'smallserial', 'serial', 'bigserial' ) THEN '1' || '::' || att1.data_type WHEN att1.data_type IN ( 'decimal', 'numeric', 'real', 'double precision' ) THEN '99.99' || '::' || att1.data_type WHEN att1.data_type IN ('money') THEN '99.07' || '::' || att1.data_type WHEN att1.data_type IN ( 'character', 'character varying', 'varchar', 'char', 'text' ) THEN '''' || 1 || '''' || '::' || att1.data_type WHEN att1.data_type IN ('bytea') THEN 'E' || '''' || '\\000' || '''' || '::bytea' WHEN att1.data_type IN ( 'date', 'time with time zone', 'time without time zone', 'timestamp with time zone', 'timestamp without time zone' ) THEN '''' || 'now' || '''' || '::' || att1.data_type WHEN att1.data_type IN ('boolean') THEN 'true::boolean' WHEN att1.data_type IN ('UUID') THEN 'gen_random_uuid()' 
                        WHEN att1.data_type IN ('ARRAY')  -- support nested array
                        THEN (select 'ARRAY[ROW(' || STRING_AGG( CASE WHEN att2.data_type IN ( 'smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision', 'smallserial', 'serial', 'bigserial' ) THEN '1' || '::' || att2.data_type WHEN att2.data_type IN ( 'decimal', 'numeric', 'real', 'double precision' ) THEN '99.99' || '::' || att2.data_type WHEN att2.data_type IN ('money') THEN '99.07' || '::' || att2.data_type WHEN att2.data_type IN ( 'character', 'character varying', 'varchar', 'char', 'text' ) THEN '''' || 1 || '''' || '::' || att2.data_type WHEN att2.data_type IN ('bytea') THEN 'E' || '''' || '\\000' || '''' || '::bytea' WHEN att2.data_type IN ( 'date', 'time with time zone', 'time without time zone', 'timestamp with time zone', 'timestamp without time zone' ) THEN '''' || 'now' || '''' || '::' || att2.data_type WHEN att2.data_type IN ('boolean') THEN 'true::boolean' WHEN att2.data_type IN ('UUID') THEN 'gen_random_uuid()' WHEN att2.data_type IN ('ARRAY')  THEN 'NULL' WHEN att2.data_type IN ('USER-DEFINED') THEN 'NULL::' || att2.attribute_udt_schema || '.' || substr(att2.attribute_udt_name,strpos(att2.attribute_udt_name,'_')+1,length(att2.attribute_udt_name))  ELSE '' END, ',' ) || ')::' || att2.udt_schema || '.' || att2.udt_name || ']::' || att2.udt_schema || '.' || att2.udt_name || '[]' from information_schema.attributes att2 where att2.udt_schema = att1.attribute_udt_schema and att2.udt_name = substr(att1.attribute_udt_name,strpos(att1.attribute_udt_name,'_')+1,length(att1.attribute_udt_name)) GROUP BY att2.udt_schema, att2.udt_name)
                        WHEN att1.data_type IN ('USER-DEFINED')  --support nested type
                        THEN (select 'ROW(' || STRING_AGG( CASE WHEN att2.data_type IN ( 'smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision', 'smallserial', 'serial', 'bigserial' ) THEN '1' || '::' || att2.data_type WHEN att2.data_type IN ( 'decimal', 'numeric', 'real', 'double precision' ) THEN '99.99' || '::' || att2.data_type WHEN att2.data_type IN ('money') THEN '99.07' || '::' || att2.data_type WHEN att2.data_type IN ( 'character', 'character varying', 'varchar', 'char', 'text' ) THEN '''' || 1 || '''' || '::' || att2.data_type WHEN att2.data_type IN ('bytea') THEN 'E' || '''' || '\\000' || '''' || '::bytea' WHEN att2.data_type IN ( 'date', 'time with time zone', 'time without time zone', 'timestamp with time zone', 'timestamp without time zone' ) THEN '''' || 'now' || '''' || '::' || att2.data_type WHEN att2.data_type IN ('boolean') THEN 'true::boolean' WHEN att2.data_type IN ('UUID') THEN 'gen_random_uuid()' WHEN att2.data_type IN ('USER-DEFINED') THEN 'NULL::' || att2.attribute_udt_schema || '.' || substr(att2.attribute_udt_name,strpos(att2.attribute_udt_name,'_')+1,length(att2.attribute_udt_name))  ELSE '' END, ',' ) || ')::' || att2.udt_schema || '.' || att2.udt_name from information_schema.attributes att2 where att2.udt_schema = att1.attribute_udt_schema and att2.udt_name = substr(att1.attribute_udt_name,strpos(att1.attribute_udt_name,'_')+1,length(att1.attribute_udt_name)) GROUP BY att2.udt_schema, att2.udt_name)
                  ELSE '' END, ',' ) || ')::' || att1.udt_schema || '.' || att1.udt_name from information_schema.attributes att1 where att1.udt_schema = parameters.udt_schema and att1.udt_name = parameters.udt_name GROUP BY att1.udt_schema, att1.udt_name)
                  WHEN parameters.data_type IN ('ARRAY') THEN  'NULL'
                  ELSE ' ' 
          END , ',' ORDER BY parameters.ordinal_position) 
                    || COALESCE((SELECT ',' || string_agg(outparams.parameter_name   ,  ',' order by  outparams.ordinal_position)
            FROM information_schema.parameters outparams
            WHERE outparams.parameter_mode IN ('OUT','INOUT')
            AND outparams.specific_schema = routines.specific_schema
            AND outparams.specific_name = routines.specific_name
            ),' ')
                    || ');' || e'\n'
                    || 'END $$'
                     AS "sql_command" 
FROM      information_schema.routines 
left join information_schema.parameters 
ON        routines.specific_name=parameters.specific_name 
AND       parameters.parameter_mode NOT IN ('OUT') 
WHERE     routines.specific_schema=lower('<<postgres_schema_name>>')
AND       routines.routine_type IN ('PROCEDURE' , 
                                    'FUNCTION') 
AND       ( 
                    routines.data_type NOT IN ('trigger' , 
                                               'event_trigger') 
          OR        routines.data_type IS NULL) 
GROUP BY  routines.routine_name , 
          routines.routine_type , 
          routines.specific_schema ,
          routines.specific_name
ORDER BY  routines.routine_name;

