select *
from {{ source('source', 'yellow_tripdata_sample_2019-01') }}
