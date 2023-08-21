from datetime import datetime
import os
import psutil

class Logger:

    def __init__(self, output_dir = "./", active = True, name = "General"):
        
        # Turn on / Turn off logging
        self.active = active

        # Create the output file
        log_file_name = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{name}.txt"
        self.output_file = os.path.join(output_dir, log_file_name)
        self.log(f"Logger {name} started.")

    def log(self, message, mark = "[INFO]"):
        if self.active:
            with open(self.output_file, "a") as file:
                file.writelines(f"{datetime.now()}-{mark}: {message}\n")

    # For any methods below, use self.log(message)
    # ----------
    def log_memory(self):
        memory = psutil.virtual_memory()
        message = f"Available: {round(memory.available * 1e-9, 2)} Gb, used: {memory.percent}% of total."
        self.log(message)

    def log_cat(self):
        message = "≽^•⩊•^≼"
        self.log(message)

