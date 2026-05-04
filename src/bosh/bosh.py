import msvcrt

class Main:
    def run(self):
        print("Hello from bosh!")
        print("Press any key to continue...")
        msvcrt.getch()




# Entry point for command line execution
if __name__ == "__main__":
    Main().run()

# Alternative entry point for uv
def main():
    Main().run()