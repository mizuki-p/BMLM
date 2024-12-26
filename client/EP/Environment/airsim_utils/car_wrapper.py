import EP.Environment.airsim_utils.setup_path
import EP.Environment.airsim_utils.airsim as airsim
import math, random, time
import numpy as np
import os
import base64
import cv2
import copy

# objects_dict = {
#     "turbine1": "BP_Wind_Turbines_C_1",
#     "turbine2": "StaticMeshActor_2",
#     "solarpanels": "StaticMeshActor_146",
#     "crowd": "StaticMeshActor_6",
#     "car": "StaticMeshActor_10",
#     "tower1": "SM_Electric_trellis_179",
#     "tower2": "SM_Electric_trellis_7",
#     "tower3": "SM_Electric_trellis_8",
# }

class CarWrapper:
    def __init__(self):        
        pass
    
    def init(self):
        self.car = airsim.CarClient()
        self.car.confirmConnection()
        self.car.enableApiControl(True)
        self.car.armDisarm(True)
        self.control_template = airsim.CarControls()
        
        self.GLOBAL_OFF_X = 40
        self.GLOBAL_OFF_Y = 3
    # throttle = 0.0 #正负速度
    # steering = 0.0 #方向盘角度
    # brake = 0.0 #刹车强度
    # handbrake = False #启用手刹
    # is_manual_gear = False #否使用手动挡
    # manual_gear = 0 # 手动挡位
    # gear_immediate = True #
        

    def brake(self):
        car_controls = copy.deepcopy(self.control_template)
        car_controls.throttle = 0
        car_controls.brake = 1
        self.car.setCarControls(car_controls)
        # while self.car.getCarState().speed > 0.1:
        #     self.car.setCarControls(car_controls)    
    
    def get_yaw(self,):
        orientation_quat = self.car.simGetVehiclePose().orientation
        yaw = airsim.to_eularian_angles(orientation_quat)[2]
        return math.degrees(yaw) + 180

    def set_yaw(self, target_degree):
        target_degree = target_degree % 360
        car_controls = copy.deepcopy(self.control_template)
        current_degree = self.get_yaw()
        while abs(current_degree - target_degree) > 1:
            current_degree = self.get_yaw()
            # print("Current Yaw: {%.2f}, Target Yaw: {%.2f}, Speed: {%.2f}" % (current_degree, target_degree, self.car.getCarState().speed))
            car_controls.throttle = 0.35
            
            if (target_degree > current_degree and target_degree < min(current_degree + 180, 360)) or (target_degree < current_degree + 180 - 360):
                car_controls.steering = 1
            else:
                car_controls.steering = -1
            self.car.setCarControls(car_controls)
            # time.sleep(0.1)
        car_controls.steering = 0
        car_controls.throttle = 0
        self.car.setCarControls(car_controls)
        
    def set_speed(self, speed):
        car_controls = copy.deepcopy(self.control_template)
        car_controls.steering = 0
        time = 0
        while time < 20000:
            if self.car.getCarState().speed > speed:
                car_controls.throttle = -0.5
            else:
                car_controls.throttle = 0.5
            self.car.setCarControls(car_controls)
            time += 1       
        car_controls.steering = 0
        car_controls.throttle = 0
        self.car.setCarControls(car_controls) 
            
    
    def get_car_position(self):
        # return self.get_position('test1_car')
        pose = self.car.simGetVehiclePose()
        return [pose.position.x_val + self.GLOBAL_OFF_X, pose.position.y_val + self.GLOBAL_OFF_Y, pose.position.z_val]
            
    def get_position(self, object_name):
        query_string = object_name + ".*"
        object_names_ue = []
        while len(object_names_ue) == 0:
            object_names_ue = self.car.simListSceneObjects(query_string)
        pose = self.car.simGetObjectPose(object_names_ue[0])
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]
        
        
    def go_to(self, x, y, speed=3):
        car_controls = copy.deepcopy(self.control_template)
        while True:
            current_position = self.get_car_position()              
            if math.sqrt((current_position[0] - x) ** 2 + (current_position[1] - y) ** 2) < 1:
                break
            
            target_degree = math.degrees(math.atan2(y - current_position[1], x - current_position[0])) + 180
            if abs(self.get_yaw() - target_degree) > 2:
                self.set_yaw(target_degree)            
            
            if self.car.getCarState().speed < speed:
                car_controls.brake = 0
                car_controls.throttle = 0.5
            else:
                car_controls.brake = 0.5
                car_controls.throttle = 0
                
            # print("Current Position: ", current_position)
                
            self.car.setCarControls(car_controls)
        
        while self.car.getCarState().speed > 0.1:
            car_controls.throttle = 0
            car_controls.steering = 0
            car_controls.brake = 0.6
            self.car.setCarControls(car_controls)
            
    def go_forward(self, distance, speed=3):
        car_controls = copy.deepcopy(self.control_template)
        x, y = self.get_car_position()[:2]   
        while True:
            current_position = self.get_car_position()              
            if math.sqrt((current_position[0] - x) ** 2 + (current_position[1] - y) ** 2) > distance:
                break
            
            if self.car.getCarState().speed < speed:
                car_controls.brake = 0
                car_controls.throttle = 0.5
            else:
                car_controls.brake = 0.5
                car_controls.throttle = 0
                
            # print("Current Position: ", current_position)
            self.car.setCarControls(car_controls)
        
        while self.car.getCarState().speed > 0.1:
            car_controls.throttle = 0
            car_controls.steering = 0
            car_controls.brake = 1
            self.car.setCarControls(car_controls)
            
    def go_backward(self, distance):
        car_controls = copy.deepcopy(self.control_template)
        x, y = self.get_car_position()[:2]   
        while True:
            current_position = self.get_car_position()              
            if math.sqrt((current_position[0] - x) ** 2 + (current_position[1] - y) ** 2) > distance:
                break
            
            if self.car.getCarState().speed < 1:
                car_controls.brake = 0
                car_controls.is_manual_gear = True
                car_controls.manual_gear = -1
                car_controls.throttle = -0.2
            else:
                car_controls.brake = 0.5
                car_controls.throttle = 0
                
            # print("Current Position: ", current_position)
            self.car.setCarControls(car_controls)
        
        while abs(self.car.getCarState().speed) > 0.1:
            # print(self.car.getCarState().speed)
            car_controls.throttle = 0
            car_controls.steering = 0
            car_controls.brake = 0.5
            car_controls.is_manual_gear = False
            car_controls.manual_gear = 0
            self.car.setCarControls(car_controls)

    
    def query_image(self):
        responses = self.car.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])  #scene vision image in uncompressed RGBA array
        response = responses[0]

        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 
        # reshape array to 4 channel image array H X W X 4
        img_rgb = img1d.reshape(response.height, response.width, 3)
        # original image is fliped vertically
        # img_rgb = np.flipud(img_rgb)
        # airsim.write_png(os.path.normpath('car_image.png'), img_rgb) 

        return img_rgb
        # height, width, _ = img_rgb.shape
        # # 只保存下半部分
        # image_cropped = img_rgb[int(height/2):height, 0:width]
        # # 保存裁剪后的图像
        # cv2.imwrite('./car_image.png', img_rgb)
        # cv2.imwrite('./car_image_cor.png', image_cropped)
        
       
    
    def detect_person(self):
        response = self.query_image("Is there any humanoid robot in the image either standing or lying down? Give confidence from 0-5, if confidence is higher than 2 answer 'Yes', otherwise answer 'No'.")
        # print(response)
        if 'Yes' in response or 'yes' in response:
            return True
        return False
    
    def explore(self, target_pos=None):
        while True:
            # cur_pos = self.get_drone_position()
            # x_delta, y_delta = (3 + np.random.rand(1)[0] * 5) * (1 if np.random.rand(1)[0] > 0.5 else -1), (3 + np.random.rand(1)[0] * 5) * (1 if np.random.rand(1)[0] > 0.5 else -1)
            # self.fly_to([cur_pos[0] + x_delta, cur_pos[1] + y_delta, cur_pos[2]])
            
            yaw = random.randint(0, 360) - 180
            if target_pos:
                yaw = math.degrees(math.atan2(target_pos[1] - self.get_car_position()[1], target_pos[0] - self.get_car_position()[0])) + random.randint(-10, 10)
            # self.set_yaw(yaw)
            # time.sleep(2)
            distance = 4 + np.random.rand(1)[0] * 2  # meters
            while True:
                # calculate target x,y,z
                target_x = self.get_car_position()[0] + distance * np.cos(math.radians(yaw))
                target_y = self.get_car_position()[1] + distance * np.sin(math.radians(yaw))
                
                break
                # 避障
                # if is_point_in_quadrilateral(target_x, target_y, quad):
                #     break
                
                # print('out of range:{},{}'.format(target_x, target_y))
                
                yaw = random.randint(0, 360) - 180
                if target_pos:
                    yaw = math.degrees(math.atan2(target_pos[1] - self.get_car_position()[1], target_pos[0] - self.get_car_position()[0])) + random.randint(-15, 15)
                # self.set_yaw(yaw)
                # time.sleep(2)
                distance = 3+ np.random.rand(1)[0] * 2  # meters
            
            
            self.go_to(target_x, target_y, speed=2)
            # print('fly to:{},{},{}'.format(target_x, target_y, self.get_drone_position()[2]))
            
            with open('car_comm.txt', 'a+') as f:
                f.seek(0)
                res = f.read()
                if res == '1':
                    break
        
            if self.detect_person():
                print('find person')
                break
            
            if target_pos and np.linalg.norm(np.array(self.get_car_position()[:2]) - np.array(target_pos)) < 2:
                print('suspicious area!\n Calling drone to check it.')
                with open('drone_comm.txt', 'w') as f:
                    f.write('1')
                break
    

# car = CarWrapper()
# # car.car.reset()
# # # deg = car.get_yaw()
# # # car.set_yaw(deg + 300)

# # # car.set_speed(3)

# # print(car.get_car_position())

# # car.go_to(-10,30,5)

# # print(car.query_image("What is the car doing?"))
# # car.car.enableApiControl(False)

# print(car.control_template)
# # copy
# a = copy.deepcopy(car.control_template)
# a.throttle = 0.5
# print(car.control_template)

# print(car.get_car_position())
# print(car.get_position("test1_car"))
# car.go_forward(3)
# print(car.get_car_position())
# print(car.get_position("test1_car"))
