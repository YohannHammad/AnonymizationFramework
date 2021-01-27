

class Logger:
    def __init__(self, output, to_file, printout=False):
        self.to_file = to_file
        self.print_out = printout
        if self.to_file:
            self.file = open(output, 'w+')

    def write(self, message):
        msg = "{}".format(message)
        if self.to_file:
            self.file.write(msg + "\n")
        if self.print_out:
            print(msg)

    def end(self):
        if self.to_file:
            self.file.close()