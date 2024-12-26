import EP.Environment.airsim_utils.setup_path
import EP.Environment.airsim_utils.airsim as airsim
import math, time, random
import numpy as np
import cv2

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


class DroneWrapper:
    def __init__(self):
        pass
        
    def init(self):
        # self.cv = airsim.VehicleClient()
        # self.cv.confirmConnection()
        

        self.drone = airsim.MultirotorClient()
        self.drone.reset()
        self.drone.confirmConnection()
        self.drone.enableApiControl(True)
        self.drone.armDisarm(True)

        self.GLOBAL_OFF_X = 0
        self.GLOBAL_OFF_Y = 0

        self.car = airsim.CarClient()
        # self.car.confirmConnection()
        # self.car.enableApiControl(True)
        # self.car.armDisarm(True)

    def takeoff(self):
        self.drone.takeoffAsync().join()

    def land(self):
        self.drone.landAsync().join()

    def get_drone_position(self):
        # return self.get_position("test3_drone")
        pose = self.drone.simGetVehiclePose()
        return [
            pose.position.x_val + self.GLOBAL_OFF_X,
            pose.position.y_val + self.GLOBAL_OFF_Y,
            pose.position.z_val,
        ]

    def fly_to(self, point):
        # if point[2] > 0:
        #     self.drone.moveToPositionAsync(point[0], point[1], -point[2], 5).join()
        # else:
        #     self.drone.moveToPositionAsync(point[0], point[1], point[2], 5).join()
        self.drone.moveToPositionAsync(
            point[0] - self.GLOBAL_OFF_X, point[1] - self.GLOBAL_OFF_Y, point[2], 3
        ).join()

    def fly_path(self, points):
        airsim_points = []
        for point in points:
            if point[2] > 0:
                airsim_points.append(airsim.Vector3r(point[0], point[1], -point[2]))
            else:
                airsim_points.append(airsim.Vector3r(point[0], point[1], point[2]))
        self.drone.moveOnPathAsync(
            airsim_points,
            5,
            120,
            airsim.DrivetrainType.ForwardOnly,
            airsim.YawMode(False, 0),
            20,
            1,
        ).join()

    def set_yaw(self, yaw):
        # print(yaw)
        # yaw = (yaw + 180 + 360) % 360 - 180
        self.drone.rotateToYawAsync(yaw, 2).join()

    def get_yaw(self):
        # TODO 获得的角度不变，一直是初始位置？
        orientation_quat = self.drone.simGetVehiclePose().orientation
        yaw = airsim.to_eularian_angles(orientation_quat)[2]
        # print(yaw)
        return yaw

    def get_position(self, object_name):
        if object_name == "test1_car":
            pose = self.car.simGetVehiclePose()
            return [pose.position.x_val, pose.position.y_val, pose.position.z_val]

        query_string = object_name + ".*"
        object_names_ue = []
        while len(object_names_ue) == 0:
            object_names_ue = self.drone.simListSceneObjects(query_string)
        pose = self.drone.simGetObjectPose(object_names_ue[0])
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]

    def query_image(self):
        responses = self.drone.simGetImages(
            [airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)]
        )  # scene vision image in uncompressed RGBA array
        response = responses[0]

        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgb = img1d.reshape(response.height, response.width, 3)
        # original image is fliped vertically
        # img_rgb = np.flipud(img_rgb)
        # airsim.write_png(os.path.normpath('drone_image.png'), img_rgb)

        # height, width, _ = img_rgb.shape
        # # 计算裁剪区域的大小（正方形边长为最小边长）
        # side_length = 720
        # # 计算裁剪区域的起始坐标（从中心向四周扩展）
        # top = (height - side_length) // 2
        # left = (width - side_length) // 2
        # # 裁剪出图像的中心正方形部分
        # image_cropped = img_rgb[top : top + side_length, left : left + side_length]
        # # 保存裁剪后的图像
        # cv2.imwrite("./drone_image.png", img_rgb)
        # cv2.imwrite("./drone_image_cor.png", image_cropped)


        # bgr_image = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        return img_rgb


    def detect_person(self):
        response = self.query_image(
            "Is there any humanoid robot in the image either standing or lying down? Give confidence from 0-5, if confidence is higher than 3 answer 'Yes', otherwise answer 'No'."
        )
        # print(response)
        if "Yes" in response or "yes" in response:
            return True
        return False

    def explore(self, target_pos=None, flg=False):
        def is_point_in_quadrilateral(px, py, quad):
            """
            Check if a point (px, py) is inside a quadrilateral defined by the list of points quad.
            quad should be a list of four tuples [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
            """

            def sign(p1, p2, p3):
                return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (
                    p1[1] - p3[1]
                )

            b1 = sign((px, py), quad[0], quad[1]) < 0.0
            b2 = sign((px, py), quad[1], quad[2]) < 0.0
            b3 = sign((px, py), quad[2], quad[3]) < 0.0
            b4 = sign((px, py), quad[3], quad[0]) < 0.0

            return (b1 == b2) and (b2 == b3) and (b3 == b4)

        # Define the quadrilateral vertices
        quad = [(80, -15), (88, 18), (15, 20), (15, -24)]

        while True:
            # cur_pos = self.get_drone_position()
            # x_delta, y_delta = (3 + np.random.rand(1)[0] * 5) * (1 if np.random.rand(1)[0] > 0.5 else -1), (3 + np.random.rand(1)[0] * 5) * (1 if np.random.rand(1)[0] > 0.5 else -1)
            # self.fly_to([cur_pos[0] + x_delta, cur_pos[1] + y_delta, cur_pos[2]])

            yaw = random.randint(0, 360) - 180
            if target_pos:
                yaw = math.degrees(
                    math.atan2(
                        target_pos[1] - self.get_drone_position()[1],
                        target_pos[0] - self.get_drone_position()[0],
                    )
                ) + random.randint(-30, 30)
            self.set_yaw(yaw)
            time.sleep(2)
            distance = 3 + np.random.rand(1)[0] * 0.5  # meters
            while True:
                # calculate target x,y,z
                target_x = self.get_drone_position()[0] + distance * np.cos(
                    math.radians(yaw)
                )
                target_y = self.get_drone_position()[1] + distance * np.sin(
                    math.radians(yaw)
                )
                # if in valid area
                if is_point_in_quadrilateral(target_x, target_y, quad):
                    break

                # print('out of range:{},{}'.format(target_x, target_y))

                yaw = random.randint(0, 360) - 180
                if target_pos:
                    yaw = math.degrees(
                        math.atan2(
                            target_pos[1] - self.get_drone_position()[1],
                            target_pos[0] - self.get_drone_position()[0],
                        )
                    ) + random.randint(-30, 30)
                self.set_yaw(yaw)
                time.sleep(2)
                distance = 3 + np.random.rand(1)[0] * 0.5  # meters

            # velocity = 3  # meters per second
            # duration = distance / velocity
            # self.drone.moveByVelocityBodyFrameAsync(velocity, 0, 0, duration).join()

            self.fly_to([target_x, target_y, -10])
            # print('fly to:{},{},{}'.format(target_x, target_y, self.get_drone_position()[2]))
            time.sleep(4)

            with open("drone_comm.txt", "a+") as f:
                f.seek(0)
                res = f.read()
                if res == "1":
                    # clear 1
                    f.seek(0)
                    f.truncate()
                    f.write("0")
                    break

            # if self.detect_person():
            #     print('find person')
            #     break

            # arrive tagert position
            if (
                target_pos
                and np.linalg.norm(
                    np.array(self.get_drone_position()[:2]) - np.array(target_pos)
                )
                < 2
            ):
                print("suspicious area!\n Calling car to check it.")
                if flg:
                    with open("car_comm.txt", "w") as f:
                        f.write("1")
                break


# Person1:[24.829999923706055, 14.029999732971191, 2.0899999141693115]
# Person2:[34.48941421508789, -9.017088890075684, 1.022295355796814]
# Person3:[67.65999603271484, -12.519999504089355, 2.0799999237060547]
# Person4:[69.95999908447266, 12.399999618530273, 2.0899999141693115]
# lf  80,-15,-10
# rf: 88,18,-10
# rb: 15,20,-10
# lb: 15,-24,-10


# drone = DroneWrapper()
# print(drone.get_drone_position())
# print(drone.get_position("test3_drone"))
# drone.takeoff()
# drone.fly_to([5, 5, 4])
# print(drone.get_drone_position())
# print(drone.get_position("test3_drone"))
