/*


Version: 1.0
Date: 2022-10-21

*/

DECLARE 

   target_engine varchar2(1000):= 'POSTGRESQL';
 
 
   /*It control percentage of table data to sampled to generate data characteristics and make data driven decision for number without precision and scale*/
   scan_max_table_perc number := '25';
 
 
   /*It controls whether to scan data for all NUMBER data types including NUMBER declaration with precision and scale defined. It is set default as N*/
   scan_data_for_all_number_col CHAR(1):= 'N';
 
   /*It control whether set all number with declaration as number(p) to in*/
   opti_number_def_without_scale CHAR(1):= 'N';
 
   /*It controls whether to scan data for  NUMBER data type declaration without precision and scale defined.
   If sets to N, it will sampled gather statistics and recommend target data type only based on High and Low value*/
   scan_data_without_prec_scale CHAR(1) := 'Y';
 
   /*It controls the scan method on the Oracle table and if parallel needs to be enabled with how many threads.*/
   oracle_table_parallel_degree integer := 2;

    min_value number;
    max_value number;
    max_precision number;
    max_scale number;
    --Add schema name to be scan for number data type recommender.
    schemaname varchar2(4000) := '<<ORACLE_SCHEMA_NAME>>'; --'SCHEMA Name one at a time.';
    --Add semicolon(;) separated list of table name or add wildcard % to scan all table in the specified schema.
    tablename varchar2(4000) := '%';  --'%'; 

    modify_type VARCHAR2(4000) := NULL;
    all_modify_type  VARCHAR2(32767) := NULL;
    low_stats_value varchar2(4000) := null;
    high_stats_value varchar2(4000) := null;
    from_str varchar2(32767) := null;
    TYPE number_mapping IS RECORD 
    (
        OWNER VARCHAR(4000),
        TABLE_NAME VARCHAR(4000),
        APPROX_NUM_ROWS NUMBER,
        ROWS_SAMPLE NUMBER,
        COLUMN_NAME VARCHAR(4000),
        target_pg_datatype VARCHAR(4000),
        MIN_VAL VARCHAR(4000),
        MAX_VAL VARCHAR(4000),
        MAX_PRECISION VARCHAR(4000),
        MAX_SCALE VARCHAR(4000)
    );
    rec_number_mapping number_mapping;
    cursor1 SYS_REFCURSOR;

    CURSOR cur_number_dt IS 
    WITH alias1 
        AS (SELECT atc.owner 
                    table_schema, 
                    atc.table_name, 
                    (SELECT NUM_ROWS FROM ALL_TABLES WHERE ALL_TABLES.OWNER = atc.owner AND ALL_TABLES.TABLE_NAME = atc.table_name) APPROX_NUM_ROWS,                                       
                    atc.column_name, 
                    atc.data_type, 
                    atc.data_precision, 
                    atc.data_scale, 
                    to_char(utl_raw.cast_to_number(atc.low_value)) low_stats_value, 
                    to_char(utl_raw.cast_to_number(atc.high_value)) high_stats_value,
                    '''' || atc.column_name || '''' || ' AS C_NAME_' || upper(atc.column_name)
                    || ', MIN(' 
                    || '"' || atc.column_name || '"' 
                    || ') AS MIN_VAL_' || upper(atc.column_name) || ' , MAX(' 
                    || '"' || atc.column_name || '"' 
                    || ') AS MAX_VAL_' || upper(atc.column_name) || ' ,MIN((INSTR(TO_CHAR(' 
                    || 'CASE WHEN INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || ')' 
                    || ',' 
                    || '''' 
                    || '.' 
                    ||'''' 
                    || ') > 0 THEN ' 
                    || '"' || atc.column_name || '"' 
                    || ' ELSE NULL END ) ,' 
                    ||'''' 
                    || '.' 
                    || '''' 
                    || ')-1)) AS MIN_PREC_' || upper(atc.column_name) || ' ,MAX((INSTR(TO_CHAR(' 
                    || 'CASE WHEN INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || ')' 
                    || ',' 
                    || '''' 
                    || '.' 
                    ||'''' 
                    || ') > 0 THEN ' 
                    || '"' || atc.column_name || '"' 
                    || ' ELSE NULL END ) ,' 
                    ||'''' 
                    || '.' 
                    || '''' 
                    || ')-1)) AS MAX_PREC_' || upper(atc.column_name) || ' ,MIN(CASE WHEN INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || '),' 
                    || '''' 
                    || '.' 
                    || '''' 
                    || ')>0 THEN ' 
                    || 'LENGTH(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || '))-INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || '),' 
                    || '''' 
                    || '.' 
                    || '''' 
                    || ') ELSE NULL END)' 
                    ||' AS MIN_SCLE_' || upper(atc.column_name) || ' ,MAX(CASE WHEN INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || '),' 
                    || '''' 
                    || '.' 
                    || '''' 
                    || ')>0 THEN ' 
                    || 'LENGTH(TO_CHAR(' 
                    || '"' || atc.column_name || '"'  
                    || '))-INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || '),' 
                    || '''' 
                    || '.' 
                    || '''' 
                    || ')  ELSE NULL END)' 
                    ||' AS MAX_SCLE_' || upper(atc.column_name) || ' ,COUNT(CASE WHEN(LENGTH(TO_CHAR(' 
                    || '"' || atc.column_name || '"' 
                    || ')-INSTR(TO_CHAR(' 
                    || '"' || atc.column_name || '"'  
                    || '),' 
                    || '''' 
                    || '.' 
                    ||'''' 
                    ||'))) > 38 THEN 1 ELSE NULL END) AS CNT_H_SCLE' || '_' || upper(atc.column_name)  AS 
                    SQL_STRING, 
                    ' FROM ' 
                    || atc.owner 
                    || '.' 
                    || atc.table_name                                      AS 
                    FROM_STRING ,
                    '(C_NAME_' || upper(atc.column_name) || ',MIN_VAL_' || upper(atc.column_name) || 
                    ',MAX_VAL_' || upper(atc.column_name) || ',MIN_PREC_' || upper(atc.column_name) ||
                    ',MAX_PREC_' || upper(atc.column_name) || ',MIN_SCLE_' || upper(atc.column_name) ||
                    ',MAX_SCLE_' || upper(atc.column_name) || ',CNT_H_SCLE' || '_' || upper(atc.column_name) ||') AS ' || '''' || 
                    upper(atc.column_name) || '''' AS unpivot_sql
            FROM   all_tab_columns atc 
            WHERE  atc.OWNER = schemaname
            and   (tablename = '%' or atc.table_name IN 
                                    (
                                      select 
                                        UPPER(
                                          regexp_substr (str, '[^;]+', 1, level)
                                        ) 
                                      from 
                                        (
                                          SELECT 
                                            tablename AS STR 
                                          FROM 
                                            DUAL
                                        ) connect by level <= length (str) - length (
                                          replace (str, ';')
                                        ) + 1
                                    ))
            and table_name not in (select all_views.view_name from all_views where all_views.owner = atc.owner)
            AND atc.OWNER || '_' ||atc.table_name NOT IN 
            (SELECT ALL_TABLES.OWNER || '_' || ALL_TABLES.table_name  FROM ALL_TABLES WHERE 
            ALL_TABLES.OWNER =atc.OWNER AND  ALL_TABLES.TEMPORARY = 'Y')
                    AND atc.data_type IN ( 'NUMBER' ) 
                    AND ( atc.table_name NOT LIKE '%TOAD%' 
                            AND atc.table_name NOT LIKE '%PLAN_TABLE%' ) 
            ORDER  BY atc.owner, 
                        atc.table_name, 
                        atc.column_id) 
    SELECT table_schema, 
            table_name, 
            APPROX_NUM_ROWS,
            column_name, 
            data_type, 
            data_precision, 
            low_stats_value,
            high_stats_value,
            data_scale, 
            CASE 
            WHEN (data_precision IS NULL 
                    OR data_precision = 0) or scan_data_for_all_number_col = 'Y' THEN 'ACTUAL' 
            ELSE 'METADATA' 
            END                AS RUNTYPE, 
            sql_string , from_string     AS SELECT_SQL, 
            unpivot_sql,
            Row_number() 
            over ( 
                ORDER BY NULL) AS rn , 
            count(1) over (partition by table_schema , table_name) cnt_col_tbl,
            row_number() over (partition by table_schema , table_name order by null) rn_col_tbl
    FROM   alias1 ;
                            
    rect_number_dt                           cur_number_dt%ROWTYPE; 
    sqlstr                                  clob; 
    unpivot_sql                             clob := NULL;
    sqlstr1                                  clob:= NULL;
    target_pg_datatype                          VARCHAR2(4000); 
    current_table varchar2(4000) := 'EMPTY';
BEGIN 
DBMS_OUTPUT.ENABLE(1000000);
/* Decision matrix for PostgreSQL */
sqlstr := 
'SELECT ' || '/*+ PARALLEL(' || oracle_table_parallel_degree || ') */ ' 
|| ' OWNER , TABLE_NAME , APPROX_NUM_ROWS, ROWS_SAMPLE , COL_NAME AS COLUMN_NAME ' || 
', CASE WHEN MAX_SCALE IS NULL AND MIN_SCALE IS NULL AND MIN_VAL BETWEEN -2147483648 AND 2147483647 AND MAX_VAL BETWEEN -2147483648 AND 2147483647 THEN '
|| '''' 
|| 'BIGINT' 
|| '''' 
|| 
' WHEN MAX_SCALE IS NULL AND MIN_SCALE IS NULL AND MIN_VAL BETWEEN -9223372036854775808  AND 9223372036854775807 AND MAX_VAL BETWEEN -9223372036854775808  AND 9223372036854775807                                THEN '
|| '''' 
|| 'BIGINT' 
|| '''' 
|| 
' WHEN MAX_SCALE IS NOT NULL AND MIN_SCALE IS NOT NULL AND ((MAX_PRECISION + MAX_SCALE) <= 15 ) THEN '
|| '''' 
|| 'DOUBLE PRECISION'
|| '''' 
|| ' WHEN  MIN_VAL IS NULL AND MAX_VAL IS NULL THEN '
|| '''' 
|| 'DOUBLE PRECISION'
|| '''' 
|| ' ELSE ' || '''NUMERIC''' ||  ' END AS target_pg_datatype '
|| ' ,MIN_VAL ,MAX_VAL, MAX_PRECISION ,MAX_SCALE   FROM (';

OPEN cur_number_dt; 
dbms_output.Put_line ('table_schema'
                    || '*' 	
                    || 'table_name' 
                    || '*' 
                    || 'column_name'
                    || '*'
                    || 'data_type' 
                    || '*' 
                    || 'approx_num_rows'
                    || '*' 
                    || 'rows_scanned'
                    || '*'
                    || 'min_value'
                    || '*'
                    || 'max_value'
                    || '*' 
                    || 'max_precision'
                    || '*'
                    ||'max_scale' 
                    || '*'
                    || CASE WHEN target_engine LIKE '%POSTGRESQL%' THEN '*target_pg_datatype' END); 
LOOP 
    FETCH cur_number_dt INTO rect_number_dt; 
    EXIT WHEN cur_number_dt%NOTFOUND; 
    min_value := NULL;
    max_value := NULL;
    max_precision := NULL;
    max_scale := NULL;
    low_stats_value := null;
    high_stats_value := null;

IF rect_number_dt.RUNTYPE = 'ACTUAL' and scan_data_without_prec_scale = 'Y' THEN 

unpivot_sql := CASE WHEN unpivot_sql IS NULL 
                    THEN 'SELECT * FROM (
                        SELECT * FROM ALIAS1 unpivot ((COL_NAME,MIN_VAL ,MAX_VAL, MIN_PRECISION , MAX_PRECISION ,MIN_SCALE , MAX_SCALE ,CNT_H_SCLE) for p1 in (' || rect_number_dt.unpivot_sql
               ELSE unpivot_sql || ',' ||rect_number_dt.unpivot_sql
               END ;

sqlstr1 := CASE WHEN sqlstr1 IS NULL  THEN
                'WITH ALIAS1 AS (SELECT ' || '''' || rect_number_dt.table_schema || '''' || ' as owner, ' || '''' || rect_number_dt.table_name || '''' ||
                ' as table_name , COUNT(1) as ROWS_SAMPLE , ' || '''' || rect_number_dt.APPROX_NUM_ROWS || '''' || ' as APPROX_NUM_ROWS, '  ||  rect_number_dt.sql_string 
            ELSE sqlstr1 || ',' || rect_number_dt.sql_string 
            END;

from_str := ' FROM "' || rect_number_dt.table_schema || '"."' ||  rect_number_dt.table_name ||
'" SAMPLE (' || scan_max_table_perc || ') ' || ')';


ELSIF rect_number_dt.RUNTYPE = 'ACTUAL' and scan_data_without_prec_scale = 'N' THEN

low_stats_value := rect_number_dt.low_stats_value;
high_stats_value := rect_number_dt.high_stats_value;

max_precision := ( Instr(To_char(CASE
                                     WHEN Instr(low_stats_value, '.') > 0 THEN
                                     low_stats_value
                                     ELSE NULL
                                   END), '.') - 1 );
max_scale := CASE WHEN Instr(high_stats_value, '.') > 0 THEN Length(low_stats_value) - Instr(low_stats_value, '.')
                              ELSE NULL END ;

SELECT (CASE
         WHEN max_scale IS NULL
              AND min_scale IS NULL
              AND low_stats_value BETWEEN -2147483648 AND 2147483647
              AND high_stats_value BETWEEN -2147483648 AND 2147483647 THEN 'BIGINT'
         WHEN max_scale IS NULL
              AND min_scale IS NULL
              AND low_stats_value BETWEEN -9223372036854775808 AND 9223372036854775807
              AND high_stats_value BETWEEN -9223372036854775808 AND 9223372036854775807
       THEN
         'BIGINT' ELSE 'DOUBLE PRECISION' END) INTO target_pg_datatype FROM (SELECT CASE WHEN Instr(low_stats_value, '.') > 0 THEN Length(low_stats_value) - Instr(low_stats_value, '.')
                              ELSE NULL END AS MIN_SCALE, 
                         CASE WHEN Instr(high_stats_value, '.') > 0 THEN Length(low_stats_value) - Instr(low_stats_value, '.')
                              ELSE NULL END  AS MAX_SCALE   , 
                         ( Instr(To_char(CASE
                                     WHEN Instr(low_stats_value, '.') > 0 THEN
                                     low_stats_value
                                     ELSE NULL
                                   END), '.') - 1 ) AS MIN_PRECISION, 
                        ( Instr(To_char(CASE
                                     WHEN Instr(high_stats_value, '.') > 0 THEN
                                     high_stats_value
                                     ELSE NULL
                                   END), '.') - 1 ) AS MAX_PRECISION FROM DUAL);

ELSE
max_precision := rect_number_dt.data_precision;
max_scale := rect_number_dt.data_scale;

target_pg_datatype := CASE 
                         WHEN  (rect_number_dt.data_scale = 0 or rect_number_dt.data_scale is null) and rect_number_dt.data_precision < 5
                         THEN 'SMALLINT'
                         WHEN  (rect_number_dt.data_scale = 0 or rect_number_dt.data_scale is null) and rect_number_dt.data_precision >= 5 AND rect_number_dt.data_precision < 10
                         THEN 'INTEGER'
                         WHEN  (rect_number_dt.data_scale = 0 or rect_number_dt.data_scale is null) and rect_number_dt.data_precision >= 10 AND rect_number_dt.data_precision < 19
                         THEN 'BIGINT'
                         WHEN opti_number_def_without_scale = 'Y' and (rect_number_dt.data_scale = 0 or rect_number_dt.data_scale is null)
                         THEN 'BIGINT'
                         ELSE 'NUMERIC'
                         END ;

END IF;

IF scan_data_without_prec_scale = 'Y' and rect_number_dt.cnt_col_tbl = rect_number_dt.rn_col_tbl and unpivot_sql is not null THEN

    unpivot_sql := unpivot_sql || '))))';
    sqlstr1 := sqlstr || sqlstr1 || from_str  || unpivot_sql;
   --dbms_output.Put_line (sqlstr1);

    open cursor1 for sqlstr1;
        LOOP
            FETCH cursor1 INTO rec_number_mapping;
            exit when cursor1%NOTFOUND;

            dbms_output.Put_line (rec_number_mapping.owner 
                    || '*' 	
                    || rec_number_mapping.table_name 
                    || '*' 
                    || rec_number_mapping.column_name 
                    || '*' 
                    || 'NUMBER'
                    || '*'
                    || rec_number_mapping.APPROX_NUM_ROWS 
                    || '*' 
                    || rec_number_mapping.ROWS_SAMPLE
                    || '*'
                    || rec_number_mapping.MIN_VAL
                    || '*' 
                    || rec_number_mapping.MAX_VAL
                    || '*' 
                    || coalesce(rec_number_mapping.MAX_PRECISION , Length(rec_number_mapping.MAX_VAL))
                    || '*'
                    || case when rec_number_mapping.MAX_PRECISION is null then null else rec_number_mapping.MAX_SCALE end
                    || '*'
                    ||  CASE WHEN target_engine LIKE '%POSTGRESQL%' THEN  trim(rec_number_mapping.target_pg_datatype) END
                    ); 

            --ora2pg as default optimize number(*,0) declaration to PostgreSQL data type
            --ora2pg as default optimize number(*,0) declaration to PostgreSQL data type
            IF rec_number_mapping.ROWS_SAMPLE > 0 THEN
            modify_type := 
            CASE 
            WHEN modify_type IS NULL and rec_number_mapping.target_pg_datatype is not null  
            THEN  rec_number_mapping.table_name|| ':' || rec_number_mapping.column_name || ':' || trim(rec_number_mapping.target_pg_datatype) 
            ELSE 
                CASE 
                    WHEN rec_number_mapping.target_pg_datatype IS NOT NULL 
                    THEN modify_type || ',' || rec_number_mapping.table_name|| ':' || rec_number_mapping.column_name || ':' || trim(rec_number_mapping.target_pg_datatype)  
                    ELSE modify_type  
                END  
            END;
            END IF;
            -- all_modify_type := CASE WHEN LENGTH(all_modify_type) >= 1 THEN all_modify_type || ',' || modify_type ELSE modify_type END;
        end loop;
    close cursor1;   
 sqlstr1 := null;
 from_str := null ;
  unpivot_sql := null;
END IF;


IF ((rect_number_dt.RUNTYPE = 'ACTUAL' and scan_data_without_prec_scale = 'N') OR rect_number_dt.RUNTYPE = 'METADATA') THEN
dbms_output.Put_line (rect_number_dt.table_schema 
                    || '*' 	
                    || rect_number_dt.table_name 
                    || '*'
                    || rect_number_dt.column_name 
                    || '*' 
                    || rect_number_dt.data_type 
                    || '*' 
                    || rect_number_dt.APPROX_NUM_ROWS 
                    || '*' 
                    || '0'
                    || '*' 
                    || CASE WHEN rect_number_dt.RUNTYPE = 'METADATA' THEN '0' 
                            WHEN rect_number_dt.RUNTYPE = 'ACTUAL' and scan_data_without_prec_scale = 'N'
                            THEN '2'
                            END
                    || '*'
                    || min_value
                    || '*' 
                    || max_value
                    || '*' 
                    || max_precision
                    || '*'
                    || case when max_precision is null then null else max_scale end
                    || '*'
                    ||   CASE WHEN target_engine LIKE '%POSTGRESQL%' THEN  trim(target_pg_datatype) END
                    ); 



if (rect_number_dt.RUNTYPE = 'ACTUAL' and scan_data_without_prec_scale = 'N') then
modify_type := 
            CASE 
            WHEN modify_type IS NULL and target_pg_datatype != 'NUMERIC' 
            THEN  rect_number_dt.table_name || ':' || rect_number_dt.column_name  || ':' || trim(target_pg_datatype) 
            ELSE 
                CASE 
                    WHEN target_pg_datatype != 'NUMERIC'     
                    THEN modify_type || ',' || rect_number_dt.table_name || ':' || rect_number_dt.column_name  || ':' || trim(target_pg_datatype)  
                    ELSE modify_type  
                END  
            END;
end if;
END IF;


IF rect_number_dt.cnt_col_tbl = rect_number_dt.rn_col_tbl and modify_type is not null AND target_engine LIKE '%POSTGRESQL%'
THEN 

all_modify_type := CASE WHEN LENGTH(all_modify_type) >= 1 THEN all_modify_type || ',' || modify_type ELSE modify_type END ;
modify_type := Null;
END IF;


END LOOP; 

dbms_output.Put_line (rect_number_dt.table_schema 
                    || '*' 	
                    || '*'
                    ||'ORA2PG_MODIFY_TYPE'
                    || '*' 
                    || all_modify_type
                    ); 
CLOSE cur_number_dt; 

END; 
