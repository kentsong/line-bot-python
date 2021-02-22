try:
    import local_env
    local_env.initEnv()
except:
    print('warm....localEnv not found')