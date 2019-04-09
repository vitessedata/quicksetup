-- explain analyze 
select 
dg_utils.transducer_column_text(1) as filename,
dg_utils.transducer_column_int4(2) as nth, 
dg_utils.transducer_column_float4(3) as score,
dg_utils.transducer_column_text(4) as tag,
gnet(), t.*
from (
    select dir || '/' || basename from imagefiles 
    where dir like '%panda%'
    and (basename like '%jpeg' or basename like '%jpg')
) t
;

