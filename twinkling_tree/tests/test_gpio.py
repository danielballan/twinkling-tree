import RPi.GPIO as GPIO
import sys


def interactively_flip_pin(pin):
    print(f"Controlling GPIO pin {pin}")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT, initial=0)
    try:
        while True:
            GPIO.output(pin, 0)
            input("Currently low. Press ENTER to go high.")
            GPIO.output(pin, 1)
            input("Currently high. Press ENTER to go low.")
    except KeyboardInterrupt:
        print("Setting low on the way to exiting.")
        GPIO.output(pin, 0)
        GPIO.cleanup()
        print("Exiting")


def main():
    pin = int(sys.argv[1])
    interactively_flip_pin(pin)


if __name__ == "__main__":
    main()
