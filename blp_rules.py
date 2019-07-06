def enforce_blp_read(user_level, file_level):
    # Enforce BLP no read up
    return user_level.value >= file_level.value


def enforce_blp_write(user_level, file_level):
    # Enforce BLP no write down
    return user_level.value <= file_level.value
