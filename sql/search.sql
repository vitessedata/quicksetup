-- explain
with searchinput as (
    select tag from (
        select 
            dg_utils.transducer_column_text(1) as filename,
            dg_utils.transducer_column_int4(2) as nth,
            dg_utils.transducer_column_float4(3) as score, 
            dg_utils.transducer_column_text(4) as tag,
            gnet(), t.*
        from (
          select dir || '/' || basename from imagefiles where 
          dir like '%search%' and basename = 'object.jpg'
        ) t 
    ) tmpt
    where nth = 0
),
searchdataset as (
    select filename, tag
    from (
        select 
            dg_utils.transducer_column_text(1) as filename,
            dg_utils.transducer_column_int4(2) as nth, 
            dg_utils.transducer_column_float4(3) as score, 
            dg_utils.transducer_column_text(4) as tag,
            gnet(), t.*
        from (
           select dir || '/' || basename from imagefiles 
           where dir like '%101%' and basename like '%jpg'
        ) t
    ) tmpt
    where nth = 0
)
select ds.filename from searchdataset ds, searchinput si 
where ds.tag = si.tag
;
