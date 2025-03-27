def get_final_score(voice, face, body):
    return round((voice * 0.4) + (face * 0.3) + (body * 0.3), 2)
