import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math
from rclpy.callback_groups import ReentrantCallbackGroup
import matplotlib.pyplot as plt
from geometry_msgs.msg import Vector3

class Coppelia(Node):
    def __init__(self):
        super().__init__('coppelia')
        
        self.pub1 = self.create_publisher(Float32, 'r_w', 10)
        self.pub2 = self.create_publisher(Float32, 'l_w', 10)
        callback_group = ReentrantCallbackGroup()
        self.subscriber = self.create_subscription(Vector3, 'location', self.cmd_callback, 10,callback_group=callback_group)
        self.timer1 = self.create_timer(10, self.timer1_callback)
        self.timer2 = self.create_timer(0.05, self.timer2_callback)
        self.r_w = Float32()
        self.l_w = Float32()
        self.sim_pos=Vector3()
        self.timerCount = 0

        # some initializations gonna need
        self.theta0 = 0
        self.x0 = 0
        self.y0 = 0
        self.length = 0.15
        self.delta_t=0.05
        self.wheel_radius = 0.05
        self.position_X = []  # List to store positions
        self.position_Y = []  # List to store times
        self.theta = []

        self.sim_x=[]
        self.sim_y=[]

    def cmd_callback(self,data):
        self.sim_pos=data    

    def timer1_callback(self):
        self.timerCount += 1

        if self.timerCount == 4:
            self.timer1.cancel()
            self.get_logger().info('Timer 1 stopped.')

    def timer2_callback(self):
        if self.timerCount == 0:  # state 1
            self.r_w.data = 1.0
            self.l_w.data = 1.0
            self.get_logger().info("first mode ")
            self.pub1.publish(self.r_w)
            self.pub2.publish(self.l_w)

        elif self.timerCount == 1:  # state 2
            self.r_w.data = 1.0
            self.l_w.data = 1.5
            self.get_logger().info("second mode") 
            self.pub1.publish(self.r_w)
            self.pub2.publish(self.l_w)

        elif self.timerCount == 2:  # state 3
            self.r_w.data = 1.5
            self.l_w.data = 1.0
            self.get_logger().info("third mode") 
            self.pub1.publish(self.r_w)
            self.pub2.publish(self.l_w)

        elif self.timerCount == 3:  # state 4
            self.r_w.data = 1.0
            self.l_w.data = 1.0
            self.get_logger().info("last mode") 
            self.pub1.publish(self.r_w)
            self.pub2.publish(self.l_w)

        elif self.timerCount == 4:
            self.timerCount = 50  # termination
            # Plot position and time after 40 seconds
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title('mathematical model VS. sim model')
            plt.plot(self.position_X, self.position_Y)
            plt.plot(self.sim_x,self.sim_y)
            plt.show()

            self.timer2.cancel()
            self.get_logger().info('Timer 2 stopped.')

        #the following block of code for mathematcial model 

        avg_vel = ((self.r_w.data + self.l_w.data) * self.wheel_radius) / 2
        angular_vel = ((self.r_w.data - self.l_w.data) * self.wheel_radius) / self.length
        if len(self.theta) > 0:
            self.theta.append((angular_vel * self.delta_t) + self.theta[-1])
        else:
            # Handle the case when the list is empty
            self.theta.append(0)  # or any other default value

        delta_x = avg_vel * math.cos(self.theta[-1])
        delta_y = avg_vel * math.sin(self.theta[-1])

        if len(self.position_X) > 0:        # Store position X
            self.position_X.append(delta_x * self.delta_t + self.position_X[-1])
        else:
         self.position_X.append(delta_x * self.delta_t)

        if len(self.position_Y) > 0:        # Store position Y
            self.position_Y.append(delta_y * self.delta_t + self.position_Y[-1])
        else:
         self.position_Y.append(delta_x * self.delta_t)


        #the following block of code for simulation model

        self.sim_x.append(self.sim_pos.x)
        self.sim_y.append(self.sim_pos.y)


def main(args=None):
    rclpy.init(args=args)
    node = Coppelia()
    node.get_logger().info("Coppelia node started.")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
