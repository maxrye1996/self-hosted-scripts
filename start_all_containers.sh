#!/bin/bash

for subdirectory in */; do
    if [ -d "$subdirectory" ]; then
        cd "$subdirectory" || continue

        read -p "Do you want to start the docker containers in '$subdirectory' directory? (y/n): " answer

        if [[ "$answer" == [Yy] ]]; then
            docker compose up -d
        else
            echo "Skipping '$subdirectory'"
        fi

        cd ..
    fi
done
