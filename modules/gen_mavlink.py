from pymavlink import mavutil

def upload_waypoints(vehicle):
    # Create a MAVLink waypoint list
    wp = mavutil.mavlink.MAVLink_waypoint_list()

    # Add waypoints (adjust coordinates and altitude as needed)
    wp.add(mavutil.mavlink.MAVLink_mission_item_message(
        1, 0, 0, 16, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        0, 1, 0, 0, 0, 0, 47.123456, -122.987654, 10.0  # Example waypoint: lat, lon, alt
    ))

    # Upload waypoints
    vehicle.waypoint_clear_all_send()
    vehicle.waypoint_count_send(wp.count())
    msg = vehicle.recv_match(type=['MISSION_REQUEST'], blocking=True)
    vehicle.mav.send(wp.wp(msg.seq))

# Example usage:
if __name__ == "__main__":
    # Replace with your actual connection string (e.g., serial, UDP, or TCP)
    connection_string = '172.30.64.1:14550'  # Example: serial connection

    try:
        vehicle = mavutil.mavlink_connection(connection_string)
        vehicle.wait_heartbeat()
        print("Connected to vehicle.")
        upload_waypoints(vehicle)
        print("Waypoints uploaded successfully.")
    except Exception as e:
        print(f"Error: {e}")
