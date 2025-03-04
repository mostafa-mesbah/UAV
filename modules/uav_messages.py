
import pymavlink.dialects.v20.all as dialect
import csv


class uav_messages:
    def __init__(self,config_data,vehicle):
        self.vehicle = vehicle
        self.config_data = config_data

    def upload_fence(self):
            # print("upload fence from csv  file (1) \nor from .waypoint file (2)")
            # the_choice = input("Enter connection number.....  \n")
            # if the_choice == '1':
            #
            # elif the_choice == '2':

            # this is the fence cords
            fence_list = []

            # fill the fence list


            #open the json data to get the home location


            # add the return point
            lat,long=self.config_data["home_lat"],self.config_data["home_long"]
            fence_list.append([lat, long])
            # open the fence_file
            try:
                with open(self.config_data['fence_file_csv'], mode='r') as file:
                    csv_reader = csv.reader(file)
                    # Skip the header
                    next(csv_reader)
                    # Iterate over the rows and append lat, long to the coordinates list
                    for i, row in enumerate(csv_reader):
                        row = ' '.join(row).split()
                        if len(row) == 3:
                            try:
                                lat, long, alt = map(float, row)
                                print(f"Latitude: {lat}, Longitude: {long}, Altitude: {alt}")
                            except ValueError as e:
                                print(f"Error converting values: {row}. Error: {e}")
                        else:
                            print(f"Invalid row format: {row}")
                        fence_list.append([lat, long])
                        # Save the first coordinate to add it again at the end
                        if i == 0:
                            first_fence_coord = [lat, long]

            except FileNotFoundError:
                 print(f"CSV file '{self.config_data['fence_file_csv']}' not found.")
                 return
            except Exception as e:
                 print(f"An error occurred while reading the CSV file: {e}")
                 return
            if first_fence_coord:
                fence_list.append(first_fence_coord)


            FENCE_TOTAL = "FENCE_TOTAL".encode(encoding="utf-8")
            FENCE_ACTION = "FENCE_ACTION".encode(encoding="utf8")
            FENCE_ENABLE = "FENCE_ENABLE".encode(encoding = "utf-8")
            PARAM_INDEX = -1
            #function to upload the fence

            self.vehicle.wait_heartbeat()

            print("Connected to system:", self.vehicle.target_system, ", component:", self.vehicle.target_component)

            # making a request to recv message

            message = dialect.MAVLink_param_request_read_message(target_system=self.vehicle.target_system,
                                                         target_component=self.vehicle.target_component,
                                                         param_id=FENCE_ACTION,
                                                         param_index=PARAM_INDEX)

            self.vehicle.mav.send(message)

            while True:

                # wait for PARAM_VALUE message
                message = self.vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname,
                                             blocking=True)

                # convert the message to dictionary
                message = message.to_dict()

                # make sure this parameter value message is for FENCE_ACTION
                if message["param_id"] == "FENCE_ACTION":

                    # get the original fence action parameter from vehicle

                    fence_action_original = int(message["param_value"])

                    # break the loop
                    break
            # debug parameter value
            print("FENCE_ACTION parameter original:", fence_action_original)


            # now we want to set paramter FENCE_ACTION

            while True:
                message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                    target_component=self.vehicle.target_component,
                                                    param_id=FENCE_ACTION,
                                                    param_value=dialect.FENCE_ACTION_NONE,
                                                    param_type=dialect.MAV_PARAM_TYPE_REAL32)

                # now we are setting the parameter

                self.vehicle.mav.send(message)

                # now we are going to check that the parameter have been set successfully

                message = self.vehicle.recv_match(type = dialect.MAVLink_param_value_message.msgname,blocking = True)

                message = message.to_dict()


                if message["param_id"] == "FENCE_ACTION":

                    fence_action_original = int(message["param_value"])

                    print("FENCE_ACTION parameter now is :", fence_action_original)

                    break

                else :
                    print("Failed to reset FENCE_ACTION to 0, trying again")


            # now we will set FENCE_TOTAL

            while True :
                message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                    target_component=self.vehicle.target_component,
                                                    param_id=FENCE_TOTAL,
                                                    param_value=0,
                                                    param_type=dialect.MAV_PARAM_TYPE_REAL32)



                self.vehicle.mav.send(message)


                message = self.vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname,
                                     blocking=True)


                message = message.to_dict()


                if message["param_id"] == "FENCE_TOTAL":

                    # make sure that parameter value set successfully
                    if int(message["param_value"]) == 0:
                        print("FENCE_TOTAL reset to 0 successfully")

                        # break the loop
                        break

                    # should send param reset message again
                    else:
                        print("Failed to reset FENCE_TOTAL to 0")



            while True:

                # create parameter set message
                message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                            target_component=self.vehicle.target_component,
                                                            param_id=FENCE_TOTAL,
                                                            param_value=len(fence_list),
                                                            param_type=dialect.MAV_PARAM_TYPE_REAL32)

                # send parameter set message to the vehicle
                self.vehicle.mav.send(message)

                # wait for PARAM_VALUE message
                message = self.vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname,
                                            blocking=True)

                # convert the message to dictionary
                message = message.to_dict()

                # make sure this parameter value message is for FENCE_TOTAL
                if message["param_id"] == "FENCE_TOTAL":

                    # make sure that parameter value set successfully
                    if int(message["param_value"]) == len(fence_list):
                        print("FENCE_TOTAL set to {0} successfully".format(len(fence_list)))

                        # break the loop
                        break

                    # should send param set message again
                    else:
                        print("Failed to set FENCE_TOTAL to {0}".format(len(fence_list)))



            idx = 0

            while idx < len(fence_list):

                message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                      target_component=self.vehicle.target_component,
                                                      idx=idx,
                                                      count=len(fence_list),
                                                      lat=fence_list[idx][0],
                                                      lng=fence_list[idx][1])


                # send this message to vehicle
                self.vehicle.mav.send(message)

                        # create FENCE_FETCH_POINT message
                message = dialect.MAVLink_fence_fetch_point_message(target_system=self.vehicle.target_system,
                                                                    target_component=self.vehicle.target_component,
                                                                    idx=idx)

                # send this message to vehicle
                self.vehicle.mav.send(message)

                # wait until receive FENCE_POINT message
                message = self.vehicle.recv_match(type=dialect.MAVLink_fence_point_message.msgname,
                                            blocking=True)

                # convert the message to dictionary
                message = message.to_dict()

                # get the latitude and longitude from the fence item
                latitude = message["lat"]
                longitude = message["lng"]


                # check the fence point is uploaded successfully
                if latitude != 0.0 and longitude != 0:
                    # increase the index of the fence item
                    idx += 1

                    print(f"point {idx} uploaded successfully")


            print("All the fence items uploaded successfully")

            while True:

                # create parameter set message
                message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                            target_component=self.vehicle.target_component,
                                                            param_id=FENCE_ACTION,
                                                            param_value=fence_action_original,
                                                            param_type=dialect.MAV_PARAM_TYPE_REAL32)

                # send parameter set message to the vehicle
                self.vehicle.mav.send(message)

                # wait for PARAM_VALUE message
                message = self.vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname,
                                            blocking=True)

                # convert the message to dictionary
                message = message.to_dict()

                # make sure this parameter value message is for FENCE_ACTION
                if message["param_id"] == "FENCE_ACTION":

                    # make sure that parameter value set successfully
                    if int(message["param_value"]) == fence_action_original:
                        print("FENCE_ACTION set to original value {0} successfully".format(fence_action_original))

                        # break the loop
                        break

                    # should send param set message again
                    else:
                        print("Failed to set FENCE_ACTION to original value {0} ".format(fence_action_original))
            message = dialect.MAVLink_command_long_message(target_system=self.vehicle.target_system,
                                                   target_component=self.vehicle.target_component,
                                                   command=dialect.MAV_CMD_DO_FENCE_ENABLE,
                                                   confirmation=0,
                                                   param1=1,
                                                   param2=0,
                                                   param3=0,
                                                   param4=0,
                                                   param5=0,
                                                   param6=0,
                                                   param7=0)

            # send the message to the vehicle
            self.vehicle.mav.send(message)


    def clear_mission(self):
            message = dialect.MAVLink_mission_request_list_message(target_system=self.vehicle.target_system,
                                                           target_component=self.vehicle.target_component,
                                                           mission_type=dialect.MAV_MISSION_TYPE_MISSION)



            self.vehicle.mav.send(message)

            message = self.vehicle.recv_match(type=dialect.MAVLink_mission_count_message.msgname,blocking=True)

            message = message.to_dict()

            count = message["count"]
            print("Total mission item count befor:", count)

                # create mission clear all message
            message = dialect.MAVLink_mission_clear_all_message(target_system=self.vehicle.target_system,
                                                                target_component=self.vehicle.target_component,
                                                                mission_type=dialect.MAV_MISSION_TYPE_MISSION)

            # send mission clear all command to the master
            self.vehicle.mav.send(message)

            # create mission request list message
            message = dialect.MAVLink_mission_request_list_message(target_system=self.vehicle.target_system,
                                                                target_component=self.vehicle.target_component,
                                                                mission_type=dialect.MAV_MISSION_TYPE_MISSION)

            # send the message to the master
            self.vehicle.mav.send(message)

            # wait mission count message
            message = self.vehicle.recv_match(type=dialect.MAVLink_mission_count_message.msgname,
                                        blocking=True)

            # convert this message to dictionary
            message = message.to_dict()

            # get the mission item count
            count = message["count"]
            print("Total mission item count now:", count)






