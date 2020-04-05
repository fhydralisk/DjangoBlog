import random


def generate_random_phone_number():
    prefix = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152", "153",
              "155", "156", "157", "158", "159", "186", "187", "188"]
    return random.choice(prefix) + "".join(random.choice("0123456789") for i in range(8))
