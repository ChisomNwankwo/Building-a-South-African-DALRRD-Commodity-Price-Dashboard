#!/bin/bash

# run horticulture scripts

# horticulture scraper
echo "Running horticulture scraper!"
screen -dm bash -c "python /home/explore-student/internship-project-2207-09/pipeline/web-scrapers/horticulture-scraper.py; exec sh"
echo "Horticulture Scraping in progress!"

# horticulture processing
while [ ! -f /home/explore-student/internship-project-2207-09/pipeline/logs/.success_horticulture-scraper ]
do
     sleep 30
done
echo "Horticulture Scraping Completed Successfully!"
echo "Running horticulture processing!"
screen -dm bash -c "python /home/explore-student/internship-project-2207-09/pipeline/processing-scripts/horticulture_processing.py; exec sh"
echo "Horticulture Processing completed!"

exit

