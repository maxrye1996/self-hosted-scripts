import os
import yaml

# Path to directory containing sub directories
main_dir: str = "./"
# Output file for the combined Docker Compose file
output_file: str = "docker-compose.yml"

# Initialize the base structure for the combined Docker Compose file
combined_compose: dict = {
    "version": "3.4",
    "services": {},
    "volumes": {},
    "networks": {},
}

def update_volume_paths(service: dict, directory_name: str) -> dict:
    """
    Updates volume paths in a service to include the subdirectory name
    
    Args:
        service (dict): The service configuration
        directory_name (str): The directory this service was found in
        
    Returns:
        dict: Updated service with corrected volume paths
    """
    updated_service = service.copy()
    
    # Handle the 'volumes' key in services
    if "volumes" in updated_service:
        updated_volumes = []
        for volume in updated_service["volumes"]:
            if isinstance(volume, str) and ":" in volume:
                # Split the volume string into source and target
                parts = volume.split(":")
                if parts[0].startswith("./"):
                    # Replace the relative path with subdirectory-prefixed path
                    parts[0] = f"./{directory_name}/{parts[0][2:]}"
                    volume = ":".join(parts)
                updated_volumes.append(volume)
            else:
                updated_volumes.append(volume)
        updated_service["volumes"] = updated_volumes
    
    return updated_service

def update_named_volumes(volumes: dict, directory_name: str) -> dict:
    """
    Adds the directory name to named volumes intended to be stored in the sub dir
    
    Args:
        volumes (dict): The volumes found in the sub docker compose files
        directory_name (str): The directory these volumes were found in
        
    Returns:
        dict: Updated volumes with corrected paths
    """
    if not volumes:
        return {}
        
    updated_volumes = {}
    for volume_name, volume_spec in volumes.items():
        # Create a unique volume name prefixed with directory name
        new_volume_name = f"{directory_name}_{volume_name}"
        
        # Handle string-based volume definitions
        if isinstance(volume_spec, str) and volume_spec.startswith("./"):
            volume_spec = f"./{directory_name}/{volume_spec[2:]}"
        # Handle dictionary-based volume definitions
        elif isinstance(volume_spec, dict):
            if "driver_opts" in volume_spec and "device" in volume_spec["driver_opts"]:
                if volume_spec["driver_opts"]["device"].startswith("./"):
                    volume_spec["driver_opts"]["device"] = f"./{directory_name}/{volume_spec['driver_opts']['device'][2:]}"
                    
            if "source" in volume_spec and volume_spec["source"].startswith("./"):
                volume_spec["source"] = f"./{directory_name}/{volume_spec['source'][2:]}"
                
        updated_volumes[new_volume_name] = volume_spec
    
    return updated_volumes

# Process all docker-compose files
for root, dirs, files in os.walk(main_dir):
    for file in files:
        if file == "docker-compose.yml":
            # Skip the main directory if it has a compose file (to avoid recursion)
            if root == main_dir:
                continue
                
            with open(os.path.join(root, file), "r") as f:
                compose_content = yaml.safe_load(f)
                
            # Get relative directory name
            directory_name = os.path.relpath(root, main_dir)
            if directory_name == '.':
                continue  # Skip the base directory
                
            # Simplify directory name if it contains path separators
            directory_name = directory_name.replace(os.path.sep, "_")
            
            # Process services
            if "services" in compose_content:
                for service_name, service in compose_content["services"].items():
                    # Create unique service name
                    unique_service_name = f"{directory_name}_{service_name}"
                    
                    # Update volume paths in this service
                    updated_service = update_volume_paths(service, directory_name)
                    
                    # Add the updated service to our combined compose
                    combined_compose["services"][unique_service_name] = updated_service
            
            # Process volumes
            if "volumes" in compose_content:
                updated_volumes = update_named_volumes(compose_content["volumes"], directory_name)
                combined_compose["volumes"].update(updated_volumes)
            
            # Process networks
            if "networks" in compose_content:
                for network_name, network in compose_content["networks"].items():
                    # Create unique network name
                    unique_network_name = f"{directory_name}_{network_name}"
                    combined_compose["networks"][unique_network_name] = network

# Remove empty sections
for section in ["volumes", "networks"]:
    if not combined_compose[section]:
        del combined_compose[section]

# Write to file with improved formatting
with open(output_file, "w") as outfile:
    yaml.dump(combined_compose, outfile, default_flow_style=False, sort_keys=False)

print(f"Combined Docker Compose file created at: {output_file}")