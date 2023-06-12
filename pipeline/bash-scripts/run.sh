#!/bin/bash

# mount s3
# s3fs -o iam_role="ec2_access_intern_buckets" -o url="https://s3-eu-west-1.amazonaws.com/" -o endpoint=eu-west-1 -o dbglevel=info -o curldbg 2207-09-dalrrd-daily-commodity-prices-b /home/explore-student/darrld_project/internship-project-2207-09/pipeline/s3
sleep 5
echo "S3 Mounted successfully!"
# run horticulture scripts

# horticulture scraper
echo "Running horticulture scraper!"
screen -dm bash -c "python /home/explore-student/darrld_project/internship-project-2207-09/pipeline/web-scrapers/horticulture-scraper.py; exec sh"
echo "Scraping completed!"

# horticulture processing
echo "Running horticulture processing!"
until [ -f /home/explore-student/darrld_project/internship-project-2207-09/pipeline/logs/.success_horticulture-scraper ]
do
     sleep 30
done
echo "Horticulture processing Completed Successfully!"
screen -dm bash -c "python /home/explore-student/darrld_project/internship-project-2207-09/pipeline/processing-scripts/horticulture_processing.py; exec sh"
exit
