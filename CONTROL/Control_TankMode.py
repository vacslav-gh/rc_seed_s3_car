import pygame
import socket
from time import sleep

import udp_settings


# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Initialized joystick: {joystick.get_name()}")

# UDP setup
udp_ip = udp_settings.ip
udp_port = udp_settings.port



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_message(message):
    sock.sendto(message.encode(), (udp_ip, udp_port))

# Configurable dead zone
dead_zone = 0.1  # Adjust dead zone sensitivity as needed

def apply_dead_zone(value):
    if -dead_zone < value < dead_zone:
        return 0
    return value

# Recording and playback mechanisms
recording = False
replaying = False
recorded_movements = []
playback_index = 0

# Main loop
running = True
while running:
    pygame.event.pump()

    # Button states
    record_button_pressed = joystick.get_button(4)
    replay_button_pressed = joystick.get_button(5)

    # Start or stop recording
    if record_button_pressed:
        if not recording:
            recorded_movements = []  # Reset movements when starting new recording
            recording = True
            print("Recording started.")
    else:
        if recording:
            recording = False
            print("Recording stopped.")

    # Start or stop replaying
    if replay_button_pressed:
        if not replaying:
            replaying = True
            playback_index = 0  # Reset index for new replay
            print("Replay started.")
    else:
        if replaying:
            replaying = False
            print("Replay stopped.")

    # Read joystick axes and apply dead zone
    left_stick_raw = -joystick.get_axis(1)   # Vertical axis of left stick (inverted)
    right_stick_raw = joystick.get_axis(3)  # Vertical axis of right stick
    left_stick = round(apply_dead_zone(left_stick_raw), 2)
    right_stick = round(apply_dead_zone(right_stick_raw), 2)
    
    # Convert to integer for speed settings
    left_speed = int(left_stick * 255)
    right_speed = int(right_stick * 255)

    # Manage recording and replaying
    if replaying:
        if playback_index < len(recorded_movements):
            left_speed, right_speed = recorded_movements[playback_index]
            send_udp_message(f"{left_speed} {right_speed}")
            playback_index += 1
        else:
            print("Playback completed.")
            replaying = False  # Automatically stop when done
    else:
        send_udp_message(f"{left_speed} {right_speed}")
        if recording:
            recorded_movements.append((left_speed, right_speed))
            

    print(f"{left_stick} : {right_stick}    {left_speed} : {right_speed}    {len(recorded_movements)} ")

    sleep(0.01)  # Adjust for smoother or faster response

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
