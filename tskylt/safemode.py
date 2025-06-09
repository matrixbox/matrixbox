try:
    with open("logg.txt", "a") as p:
        p.write("Crashed\n")
except:
    pass
import microcontroller
microcontroller.reset()