#!/bin/bash
# mount s3
s3fs -o iam_role="ec2_access_intern_buckets" -o url="https://s3-eu-west-1.amazonaws.com/" -o endpoint=eu-west-1 -o dbglevel=info -o curldbg 2207-09-dalrrd-daily-commodity-prices-b /home/explore-student/internship-project-2207-09/pipeline/s3
sleep 5
echo "S3 Mounted successfully!"


# run horticulture scraper and perform processing in a new screen
screen -dm bash -c "sh /home/explore-student/internship-project-2207-09/pipeline/bash-scripts/horticulture_run.sh; exec sh"

# run grain scraper and perform processing in a new screen
screen -dm bash -c "sh /home/explore-student/internship-project-2207-09/pipeline/bash-scripts/grain_run.sh; exec sh"

# run livestock scraper and perform processing in a new screen
# screen -dm bash -c "sh /home/explore-student/internship-project-2207-09/pipeline/bash-scripts/livestock_run.sh; exec sh"