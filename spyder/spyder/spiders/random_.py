import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time  # Import the time module
#import matplotlib
#matplotlib.use("TkAgg")

def clock_hand(r):
    def hand(theta):
        theta = np.radians(theta)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    return hand

# Create a function to update the clock hands
def update_clock():
    while True:
        
        t = dt.datetime.now()
        h = t.hour
        m = t.minute
        s = t.second

        # Calculate theta in degrees for each hand based on the current time
        theta_h = 90 - (30 * h + 0.5 * m)
        theta_m = 90 - 6 * m
        theta_s = 90 - 6 * s

        # Calculate the (x, y) coordinates for each hand
        x_h, y_h = hour_hand(theta_h)
        x_m, y_m = minute_hand(theta_m)
        x_s, y_s = second_hand(theta_s)

        # Clear the previous plot
        plt.cla()

        # Plot the clock hands
        circle = plt.Circle((0, 0), 0.95, fill=False, color='black', linewidth=1)
        plt.gca().add_artist(circle)  # Add the circle to the plot

        for marker_hour in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            theta_marker = 90 - 360 * (marker_hour / 12)
            x_marker = 0.9 * np.cos(np.radians(theta_marker))
            y_marker = 0.9 * np.sin(np.radians(theta_marker))
            plt.text(x_marker, y_marker, str((marker_hour - 1) % 12 + 1), ha='center', va='center', fontsize=12)

        plt.plot([0, x_h], [0, y_h], label='Hour Hand', color='blue', linewidth=5)
        plt.plot([0, x_m], [0, y_m], label='Minute Hand', color='green', linewidth=3)
        plt.plot([0, x_s], [0, y_s], label='Second Hand', color='red', linewidth=2)

        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        plt.gca().set_aspect('equal')
        plt.legend(loc='upper right')

        plt.title(f"The time is: {h:02d}:{m:02d}:{s:02d}")

        plt.pause(1)  # Add a pause to give the CPU some rest
        plt.draw()  # Redraw the plot

        plt.show()
# Create the clock hands
r_h = 0.5
r_m = 0.8
r_s = 0.9
hour_hand = clock_hand(r_h)
minute_hand = clock_hand(r_m)
second_hand = clock_hand(r_s)

# Plot the clock initially
plt.figure()

if __name__ == "__main__":
    update_clock()