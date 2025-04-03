#!/bin/bash

for subdirectory in */; do
    if [ -d "$subdirectory" ]; then
        echo "Processing subdirectory: $subdirectory"
        cd "$subdirectory" || continue

        read -p "Do you want to update the docker image in this directory? (y/n): " answer

        if [[ "$answer" == [Yy] ]]; then
            docker compose pull
            docker compose up -d
        else
            echo "Skipping update for this directory."
        fi

        cd ..
    fi
done
