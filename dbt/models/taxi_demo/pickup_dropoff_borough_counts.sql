select
    pickup_borough,
    dropoff_borough,
    count(*) as trip_count
from {{ ref('trips_with_borough_name') }}
group by pickup_borough, dropoff_borough
order by trip_count desc
