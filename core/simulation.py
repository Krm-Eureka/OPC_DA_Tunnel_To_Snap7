import random

def fake_opc_data():
    return {
        "LiftPosition": random.randint(1, 10),
        "Door": random.choice(["OPEN", "CLOSE"]),
    }
