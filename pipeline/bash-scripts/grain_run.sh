#!/bin/bash


# run grain scripts

# Grain scraper
echo "Running Grain scraper!"
screen -dm bash -c "python /home/explore-student/internship-project-2207-09/pipeline/web-scrapers/grain-scraper.py; exec sh"
echo "Grain Scraping in progress!"

# Grain processing
while [ ! -f /home/explore-student/internship-project-2207-09/pipeline/logs/.success_grain-scraper ]
do
     sleep 30
done
echo "Grain Scraping Completed Successfully!"
screen -dm bash -c "python /home/explore-student/internship-project-2207-09/pipeline/processing-scripts/grain_processing.py; exec sh"
echo "Grain processing completed Successfully!"

exit

