import tkinter as tk
from tkinter import Scale, Button, Label
from threading import Thread
import time
from dmx_device_eurolite_pro import DmxDeviceEurolitePro  # Replace 'your_module_name' with the actual module name

class DMXFaderWingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DMX Fader Wing")

        # Create an instance of DmxDeviceEurolitePro
        self.dmx_device = DmxDeviceEurolitePro()

        # GUI Elements
        self.status_label = Label(root, text="Device Status: Not Started", fg="red")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.info_label = Label(root, text="Activate the device before using sliders.")
        self.info_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.sliders = []
        self.slider_values = {}  # Dictionary to store slider values
        self.start_channel = 1
        self.channels_per_column = 16
        self.current_max_channel = self.start_channel + self.channels_per_column - 1
        self.max_channels = 512
        self.num_columns = 1
        self.create_channel_columns()

        # Expand Channels button
        self.expand_button = Button(self.root, text="Expand Channels", command=self.expand_channels)
        self.expand_button.grid(row=19, column=0, columnspan=2, pady=10)

        # Start DMX device button
        self.start_button = Button(self.root, text="Start DMX Device", command=self.start_dmx_device)
        self.start_button.grid(row=20, column=0, columnspan=2, pady=10)

        # Stop DMX device button
        self.stop_button = Button(self.root, text="Stop DMX Device", command=self.stop_dmx_device)
        self.stop_button.grid(row=21, column=0, columnspan=2, pady=10)

        # init DMX device
        self.start_dmx_device()

        # Update GUI in real-time
        self.update_gui()

        # start loop of sending DMX values
        self.send_dmx_values()

    def update_gui(self):
        # Periodically update GUI elements
        for slider in self.sliders:
            if self.dmx_device.is_connected() and self.dmx_device.device_status == DmxDeviceEurolitePro.DeviceStatus.STARTED:
                self.info_label.config(text="Sliders are active.")
                self.status_label.config(text="Device Status: Started")
                self.status_label.config(fg="green")
                slider.configure(state=tk.NORMAL)
            else:
                self.info_label.config(text="Activate the device before using sliders.")
                self.status_label.config(text="Device Status: Not Started")
                self.status_label.config(fg="red")
                slider.configure(state=tk.DISABLED)

        # Schedule the next update
        self.root.after(500, self.update_gui)

    def send_dmx_values(self):
        self.dmx_device.write_complete_data()

        # Schedule the next update
        self.root.after(20, self.send_dmx_values)

    def update_dmx_value(self, channel, value):
        # Update the DMX value for the specified channel
        # self.dmx_device.set_channel_value(channel, int(value))
        self.dmx_device.update_channel_value(channel, int(value))

    def start_dmx_device(self):
        # Start the DMX device in a separate thread
        Thread(target=self.start_dmx_device_thread).start()

    def start_dmx_device_thread(self):
        # Start the DMX device
        try:
            self.dmx_device.start_device()
            print("DMX device started.")
            self.dmx_device.write_complete_data()
        except Exception as e:
            print(f"Error starting DMX device: {e}")

    def stop_dmx_device(self):
        # Stop the DMX device
        try:
            self.dmx_device.stop_device()
            print("DMX device stopped.")
        except Exception as e:
            print(f"Error stopping DMX device: {e}")            

    def create_channel_columns(self):
        cur_col = self.current_max_channel / self.channels_per_column
        for i in range(1, self.channels_per_column + 1):
            current_channel = i + self.current_max_channel - self.channels_per_column
            slider_label = Label(self.root, text=f"Channel {current_channel}")
            slider = Scale(self.root, from_=0, to=255, orient="horizontal", length=200, command=lambda value, current_channel=current_channel: self.update_dmx_value(current_channel, value))
            slider_label.grid(row=i + 2, column=int(cur_col * 4 - 3), columnspan=2, padx=10)
            slider.grid(row=i + 2, column=int(cur_col * 4 - 1), columnspan=2)
            self.sliders.append(slider)
            self.slider_values[i] = 0  # Initialize with default value

    def expand_channels(self):
        # Store current slider values
        current_values = {channel: slider.get() for channel, slider in zip(range(self.start_channel, self.max_channels + 1), self.sliders)}

        if self.current_max_channel + self.channels_per_column <= 64:
            # Expand the GUI to show the next set of channels
            self.num_columns += 1
            self.current_max_channel = self.num_columns * self.channels_per_column
            print(f'self.current_max_channel: {self.current_max_channel}')
            self.create_channel_columns()

            # Restore slider values
            for i in range(self.start_channel, self.max_channels + 1):
                self.sliders[i - 1].set(current_values.get(i, 0))

                # Update stored slider values
                self.slider_values[i] = current_values.get(i, 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = DMXFaderWingApp(root)
    root.mainloop()


